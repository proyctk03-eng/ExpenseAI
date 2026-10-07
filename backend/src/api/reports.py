"""API báo cáo thống kê."""
from datetime import date, timedelta, datetime
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from src.database import get_db
from src.models import Transaction, Category, User
from src.utils.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/summary")
def get_summary(month: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(require_permission("report:read"))):
    target_date = date.fromisoformat(month + "-01") if month else date.today()
    
    date_filter = [
        extract('year', Transaction.transaction_date) == target_date.year,
        extract('month', Transaction.transaction_date) == target_date.month,
    ]
    if not current_user.has_permission("*:*"):
        date_filter.append(Transaction.user_id == current_user.id)

    # Sử dụng outerjoin để không bỏ sót giao dịch chưa có danh mục (category_id = NULL)
    # COALESCE(Category.type, 'expense') — giao dịch không có danh mục mặc định là chi tiêu
    cat_type = func.coalesce(Category.type, "expense")
    rows = (
        db.query(cat_type.label("ctype"), func.sum(Transaction.amount))
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(*date_filter)
        .group_by("ctype")
        .all()
    )
    
    totals = {"income": 0.0, "expense": 0.0}
    for ctype, total in rows:
        totals[ctype] = float(total)

    return {
        "month": target_date.strftime("%Y-%m"),
        "total_income": totals["income"],
        "total_expense": totals["expense"],
        "balance": totals["income"] - totals["expense"],
    }

@router.get("/by_category")
def get_by_category(month: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(require_permission("report:read"))):
    target_date = date.fromisoformat(month + "-01") if month else date.today()
    
    base_filter = [
        extract('year', Transaction.transaction_date) == target_date.year,
        extract('month', Transaction.transaction_date) == target_date.month
    ]
    if not current_user.has_permission("*:*"):
        base_filter.append(Transaction.user_id == current_user.id)

    # outerjoin: bao gồm cả giao dịch chưa phân loại
    cat_name = func.coalesce(Category.name, "Chưa phân loại")
    cat_type = func.coalesce(Category.type, "expense")
    results = (
        db.query(cat_name.label("cname"), cat_type.label("ctype"), func.sum(Transaction.amount).label("total"))
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(*base_filter)
        .group_by("cname", "ctype")
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
                
    return [{"category": r[0], "type": r[1], "total": float(r[2])} for r in results]


@router.get("/monthly_trend")
def get_monthly_trend(db: Session = Depends(get_db), current_user: User = Depends(require_permission("report:read"))):
    """Xu hướng thu-chi 6 tháng gần nhất — 1 truy vấn duy nhất thay vì 12 truy vấn vòng lặp."""
    today = date.today()
    six_months_ago = today.replace(day=1) - timedelta(days=150)

    base_filter = [Transaction.transaction_date >= six_months_ago]
    if not current_user.has_permission("*:*"):
        base_filter.append(Transaction.user_id == current_user.id)

    cat_type = func.coalesce(Category.type, "expense")
    rows = (
        db.query(
            extract("year", Transaction.transaction_date).label("y"),
            extract("month", Transaction.transaction_date).label("m"),
            cat_type.label("ctype"),
            func.sum(Transaction.amount),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(*base_filter)
        .group_by("y", "m", "ctype")
        .order_by("y", "m")
        .all()
    )

    monthly: dict = {}
    for year, month, ctype, total in rows:
        key = f"{int(month):02d}/{int(year)}"
        monthly.setdefault(key, {"income": 0.0, "expense": 0.0})
        monthly[key][ctype] = float(total)

    # Đảm bảo luôn trả về đủ 6 tháng ngay cả khi không có dữ liệu
    results = []
    for i in range(5, -1, -1):
        target_month = today.month - i
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        key = f"{target_month:02d}/{target_year}"
        data = monthly.get(key, {"income": 0.0, "expense": 0.0})
        results.append({
            "month": key,
            "income": data["income"],
            "expense": data["expense"],
        })

    return results


@router.get("/export/excel")
def export_excel_report(
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("report:read")),
):
    """Xuất báo cáo tài chính chuyên nghiệp ra file Excel (.xlsx)."""
    import io
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from fastapi.responses import StreamingResponse

    target_date = date.fromisoformat(month + "-01") if month else None

    # Lấy giao dịch
    q = db.query(Transaction).outerjoin(Category, Transaction.category_id == Category.id)
    if not current_user.has_permission("*:*"):
        q = q.filter(Transaction.user_id == current_user.id)
    if target_date:
        q = q.filter(
            extract("year", Transaction.transaction_date) == target_date.year,
            extract("month", Transaction.transaction_date) == target_date.month,
        )
    transactions = q.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).all()

    # Tính toán tổng hợp
    total_income = sum(float(tx.amount) for tx in transactions if tx.category_type == "income")
    total_expense = sum(float(tx.amount) for tx in transactions if tx.category_type == "expense")
    balance = total_income - total_expense

    wb = openpyxl.Workbook()
    # Sheet 1: Danh sách giao dịch
    ws_tx = wb.active
    ws_tx.title = "Giao Dịch"

    # Header styling
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    # Tiêu đề báo cáo
    period_str = f"Tháng {target_date.strftime('%m/%Y')}" if target_date else "Toàn bộ thời gian"
    ws_tx.merge_cells("A1:F1")
    title_cell = ws_tx["A1"]
    title_cell.value = f"BÁO CÁO CHI TIẾT GIAO DỊCH EXPENSEAI - {period_str.upper()}"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="1F4E79")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_tx.row_dimensions[1].height = 30

    ws_tx.merge_cells("A2:F2")
    sub_cell = ws_tx["A2"]
    sub_cell.value = f"Người dùng: {current_user.username} | Thời điểm xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    sub_cell.font = Font(name="Calibri", size=10, italic=True, color="595959")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_tx.row_dimensions[2].height = 20

    # KPI summary box in rows 4-5
    kpis = [
        ("A4", "B4", "Tổng Thu:", total_income, "2E7D32"),
        ("C4", "D4", "Tổng Chi:", total_expense, "C62828"),
        ("E4", "F4", "Số Dư:", balance, "1565C0"),
    ]
    for lbl_col, val_col, lbl, val, col_hex in kpis:
        c_lbl = ws_tx[lbl_col]
        c_lbl.value = lbl
        c_lbl.font = Font(name="Calibri", size=10, bold=True)
        c_val = ws_tx[val_col]
        c_val.value = val
        c_val.font = Font(name="Calibri", size=11, bold=True, color=col_hex)
        c_val.number_format = '#,##0" ₫"'

    # Headers for transactions table
    tx_headers = ["STT", "Ngày", "Danh Mục", "Loại", "Mô Tả Giao Dịch", "Số Tiền"]
    row_idx = 7
    for col_idx, h in enumerate(tx_headers, start=1):
        cell = ws_tx.cell(row=row_idx, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws_tx.row_dimensions[row_idx].height = 24

    for stt, tx in enumerate(transactions, start=1):
        row_idx += 1
        ws_tx.cell(row=row_idx, column=1, value=stt).alignment = Alignment(horizontal="center")
        ws_tx.cell(row=row_idx, column=2, value=str(tx.transaction_date)).alignment = Alignment(horizontal="center")
        ws_tx.cell(row=row_idx, column=3, value=tx.category_name).alignment = Alignment(horizontal="left")
        
        type_str = "Thu nhập" if tx.category_type == "income" else "Chi tiêu"
        c_type = ws_tx.cell(row=row_idx, column=4, value=type_str)
        c_type.alignment = Alignment(horizontal="center")
        
        ws_tx.cell(row=row_idx, column=5, value=tx.description).alignment = Alignment(horizontal="left")
        
        c_amt = ws_tx.cell(row=row_idx, column=6, value=float(tx.amount))
        c_amt.number_format = '#,##0" ₫"'
        c_amt.alignment = Alignment(horizontal="right")
        if tx.category_type == "income":
            c_amt.font = Font(name="Calibri", color="2E7D32", bold=True)
        else:
            c_amt.font = Font(name="Calibri", color="C62828", bold=True)

        for c in range(1, 7):
            ws_tx.cell(row=row_idx, column=c).border = thin_border

    # Auto-adjust column width
    for col in ws_tx.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws_tx.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Save to memory stream
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"ExpenseAI_Report_{month or 'All'}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
