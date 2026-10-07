"""API xin tư vấn tài chính từ AI."""
from datetime import date, timedelta
from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from src.utils.limiter import limiter

from src.database import get_db
from src.models import Transaction, Category, User
from src.utils.dependencies import get_current_user
from src.services.ai_advice import AIAdviceService
from src.services.ai_behavior import AIBehaviorService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/advice", tags=["advice"])
advice_service = AIAdviceService()
behavior_service = AIBehaviorService()


def _build_user_financial_context(db: Session, current_user: User, months: int = 6) -> dict:
    """Xây dựng bối cảnh tài chính đầy đủ theo từng tháng (6 tháng gần nhất) và tổng hợp 90 ngày."""
    today = date.today()
    start_date = today.replace(day=1) - timedelta(days=months * 30)

    cat_name = func.coalesce(Category.name, "Chưa phân loại")
    cat_type = func.coalesce(Category.type, "expense")
    year_col = extract("year", Transaction.transaction_date).label("y")
    month_col = extract("month", Transaction.transaction_date).label("m")

    # Kiểm tra xem user có giao dịch cá nhân không
    has_user_tx = db.query(Transaction.id).filter(Transaction.user_id == current_user.id).first() is not None
    user_filter = [Transaction.transaction_date >= start_date]

    if has_user_tx or not (current_user.is_admin or current_user.has_permission("*:*")):
        user_filter.append(Transaction.user_id == current_user.id)

    rows = (
        db.query(
            year_col,
            month_col,
            cat_name,
            cat_type,
            func.sum(Transaction.amount).label("total")
        )
        .select_from(Transaction)
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(*user_filter)
        .group_by(year_col, month_col, cat_name, cat_type)
        .order_by(year_col.desc(), month_col.desc())
        .all()
    )

    monthly_breakdown = {}
    summary_90d = {"income": {}, "expense": {}}
    three_months_ago = today - timedelta(days=90)

    for y, m, cname, ctype, total in rows:
        m_key = f"{int(y):04d}-{int(m):02d}"
        if m_key not in monthly_breakdown:
            monthly_breakdown[m_key] = {
                "income": 0.0,
                "expense": 0.0,
                "balance": 0.0,
                "categories": {"income": {}, "expense": {}}
            }
        val = float(total or 0)
        monthly_breakdown[m_key]["categories"].setdefault(ctype, {})[cname] = val
        if ctype == "income":
            monthly_breakdown[m_key]["income"] += val
        else:
            monthly_breakdown[m_key]["expense"] += val

        # Tổng hợp 90 ngày cho backward compatibility
        try:
            m_date = date(int(y), int(m), 1)
            if m_date >= three_months_ago.replace(day=1):
                summary_90d.setdefault(ctype, {})[cname] = summary_90d.setdefault(ctype, {}).get(cname, 0.0) + val
        except Exception:
            pass

    sorted_months = sorted(monthly_breakdown.keys(), reverse=True)
    for m_key in sorted_months:
        item = monthly_breakdown[m_key]
        item["balance"] = round(item["income"] - item["expense"], 2)
        if item["income"] > 0:
            item["savings_rate"] = round((item["balance"] / item["income"]) * 100, 1)
        else:
            item["savings_rate"] = 0.0

    mom_comparison = {}
    if len(sorted_months) >= 2:
        curr_m, prev_m = sorted_months[0], sorted_months[1]
        c_exp = monthly_breakdown[curr_m]["expense"]
        p_exp = monthly_breakdown[prev_m]["expense"]
        c_inc = monthly_breakdown[curr_m]["income"]
        p_inc = monthly_breakdown[prev_m]["income"]
        exp_diff = c_exp - p_exp
        inc_diff = c_inc - p_inc
        mom_comparison = {
            "current_month": curr_m,
            "previous_month": prev_m,
            "expense_diff": round(exp_diff, 2),
            "expense_pct_change": round((exp_diff / p_exp * 100), 1) if p_exp > 0 else 0.0,
            "income_diff": round(inc_diff, 2),
            "income_pct_change": round((inc_diff / p_inc * 100), 1) if p_inc > 0 else 0.0,
        }

    # Tính toán các chỉ số thống kê nhiều tháng (ranking, averages) để AI trả lời nhanh chóng
    highest_expense_month = None
    highest_income_month = None
    lowest_expense_month = None
    if monthly_breakdown:
        months_with_expense = [(m, data["expense"]) for m, data in monthly_breakdown.items() if data["expense"] > 0]
        months_with_income = [(m, data["income"]) for m, data in monthly_breakdown.items() if data["income"] > 0]
        if months_with_expense:
            highest_exp = max(months_with_expense, key=lambda x: x[1])
            lowest_exp = min(months_with_expense, key=lambda x: x[1])
            highest_expense_month = {"month": highest_exp[0], "amount": highest_exp[1]}
            lowest_expense_month = {"month": lowest_exp[0], "amount": lowest_exp[1]}
        if months_with_income:
            highest_inc = max(months_with_income, key=lambda x: x[1])
            highest_income_month = {"month": highest_inc[0], "amount": highest_inc[1]}

    total_m_count = max(len(monthly_breakdown), 1)
    avg_expense = round(sum(d["expense"] for d in monthly_breakdown.values()) / total_m_count, 2)
    avg_income = round(sum(d["income"] for d in monthly_breakdown.values()) / total_m_count, 2)

    return {
        "monthly_breakdown": monthly_breakdown,
        "available_months": sorted_months,
        "current_month": today.strftime("%Y-%m"),
        "month_over_month": mom_comparison,
        "analytics": {
            "highest_expense_month": highest_expense_month,
            "lowest_expense_month": lowest_expense_month,
            "highest_income_month": highest_income_month,
            "average_monthly_expense": avg_expense,
            "average_monthly_income": avg_income,
            "total_tracked_months": len(sorted_months),
        },
        "summary_90d": summary_90d,
        "income": summary_90d["income"],
        "expense": summary_90d["expense"],
    }


@router.post("/")
@limiter.limit("5/minute")
async def get_financial_advice(
    request: Request,
    force_refresh: bool = Query(False, description="Bắt buộc làm mới không dùng cache"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy lời khuyên tài chính cá nhân hóa từ AI dựa trên 90 ngày qua."""
    financial_context = _build_user_financial_context(db, current_user, months=3)
    summary = financial_context["summary_90d"]

    if not summary["expense"] and not summary["income"]:
        raise HTTPException(
            status_code=400,
            detail="Chưa có đủ dữ liệu giao dịch trong 3 tháng qua để AI phân tích. Hãy thêm các giao dịch thu chi của bạn!"
        )

    # Chỉ gửi số liệu đã tổng hợp theo danh mục; không gửi mô tả hoặc định danh giao dịch.
    advice = await advice_service.get_advice(summary, force_refresh=force_refresh)
    return {"advice": advice}


@router.get("/monthly")
@limiter.limit("10/minute")
async def get_monthly_analysis(
    request: Request,
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$", description="Tháng cần phân tích (định dạng YYYY-MM)"),
    force_refresh: bool = Query(False, description="Bắt buộc làm mới không dùng cache"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Phân tích chi tiêu chuyên sâu theo từng tháng cụ thể với AI."""
    ctx = _build_user_financial_context(db, current_user, months=6)
    target_month = month or ctx["current_month"]
    month_data = ctx["monthly_breakdown"].get(target_month)

    if not month_data or (month_data["income"] == 0 and month_data["expense"] == 0):
        return {
            "month": target_month,
            "has_data": False,
            "available_months": ctx["available_months"],
            "analysis": f"Chưa có giao dịch thu chi nào được ghi nhận trong tháng {target_month}. Bạn hãy thêm giao dịch để AI có thể phân tích nhé!",
            "summary": {"income": 0, "expense": 0, "balance": 0, "categories": {}}
        }

    # Tìm tháng liền kề trước đó nếu có
    prev_month_data = None
    sorted_m = ctx["available_months"]
    if target_month in sorted_m:
        idx = sorted_m.index(target_month)
        if idx + 1 < len(sorted_m):
            prev_m_key = sorted_m[idx + 1]
            prev_month_data = ctx["monthly_breakdown"].get(prev_m_key)

    ai_analysis = await advice_service.get_monthly_advice(target_month, month_data, prev_month_data, force_refresh=force_refresh)
    return {
        "month": target_month,
        "has_data": True,
        "available_months": ctx["available_months"],
        "summary": month_data,
        "month_over_month": ctx["month_over_month"] if target_month == ctx["current_month"] else None,
        "analysis": ai_analysis
    }


@router.get("/behavior")
@limiter.limit("3/minute")
def analyze_user_behavior(
    request: Request,
    share_transaction_details: bool = Query(
        False,
        description="Xác nhận cho phép gửi mô tả giao dịch đã chọn tới nhà cung cấp AI.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Phân tích hành vi tiêu dùng khi người dùng đã đồng ý chia sẻ chi tiết."""
    if not share_transaction_details:
        raise HTTPException(
            status_code=403,
            detail=(
                "Tính năng này cần sự đồng ý rõ ràng vì có thể gửi mô tả giao dịch "
                "tới nhà cung cấp AI. Gọi lại với share_transaction_details=true để tiếp tục."
            ),
        )
    # Lấy 50 giao dịch gần nhất
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .limit(50)
        .all()
    )
    
    if not transactions:
        raise HTTPException(status_code=400, detail="Chưa có đủ dữ liệu giao dịch để phân tích hành vi.")
        
    # Sắp xếp lại theo chiều thuận thời gian để AI dễ nhận diện chuỗi
    transactions.reverse()
    
    log_lines = []
    for tx in transactions:
        amount_str = f"{tx.amount:,.0f}đ"
        cat = tx.category_name if tx.category_name else "Khác"
        # Chỉ lấy expense để phân tích hành vi tiêu dùng
        if tx.category_type == "expense":
            log_lines.append(f"[{tx.transaction_date}] {cat}: {tx.description} ({amount_str})")
            
    if len(log_lines) < 5:
        raise HTTPException(status_code=400, detail="Cần ít nhất 5 giao dịch chi tiêu để phân tích hành vi.")
        
    log_str = "\n".join(log_lines)
    analysis = behavior_service.analyze_behavior(log_str)
    
    return {"analysis": analysis}


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$", description="Vai trò: 'user' hoặc 'assistant'")
    content: str = Field(..., min_length=1, max_length=10000, description="Nội dung tin nhắn")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Tin nhắn gửi tới AI (tối đa 4000 ký tự)")
    history: list[ChatMessage] = Field(default_factory=list, max_length=30, description="Lịch sử hội thoại trước đó (tối đa 30 tin nhắn)")


@router.post("/chat")
@limiter.limit("15/minute")
async def chat_with_ai(
    request: Request,
    chat_req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chat trực tiếp với AI dựa trên dữ liệu giao dịch chi tiết theo từng tháng."""
    financial_context = _build_user_financial_context(db, current_user, months=6)

    if not financial_context["available_months"]:
        financial_context["note"] = "Người dùng chưa có giao dịch thu chi nào trong 6 tháng qua."

    # Chuyển đổi history thành list[dict] cho AI service (cắt ngắn nếu quá dài để tối ưu token)
    history_dicts = [{"role": m.role, "content": m.content[:4000]} for m in chat_req.history]
    reply = await advice_service.chat_with_context(chat_req.message, financial_context, history=history_dicts)
    return {"reply": reply}


@router.post("/chat_stream")
@limiter.limit("15/minute")
async def chat_with_ai_stream(
    request: Request,
    chat_req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chat trực tiếp với AI dưới dạng stream."""
    financial_context = _build_user_financial_context(db, current_user, months=6)

    if not financial_context["available_months"]:
        financial_context["note"] = "Người dùng chưa có giao dịch thu chi nào trong 6 tháng qua."

    history_dicts = [{"role": m.role, "content": m.content[:4000]} for m in chat_req.history]
    
    return StreamingResponse(
        advice_service.stream_chat_with_context(chat_req.message, financial_context, history=history_dicts),
        media_type="text/event-stream"
    )
