"""
Script tạo dữ liệu mẫu sinh viên cho hệ thống ExpenseAI.
Dữ liệu chi tiêu thực tế của một sinh viên đại học Việt Nam
trong khoảng 30 ngày gần đây.
"""
import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from datetime import date, timedelta
from decimal import Decimal

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.database import SessionLocal, init_db
from src.models import Category, Transaction, User, Role
from src.utils.security import get_password_hash


def seed_student_data():
    """Tạo dữ liệu chi tiêu mẫu của sinh viên."""
    init_db()
    db = SessionLocal()

    try:
        # Xóa dữ liệu cũ của sinh viên
        old_student = db.query(User).filter(User.username == "sinhvien").first()
        if old_student:
            db.delete(old_student)
            db.commit()

        # === Tạo tài khoản sinh viên ===
        student = User(
            username="sinhvien",
            email="sinhvien@university.edu.vn",
            hashed_password=get_password_hash("123456")
        )
        user_role = db.query(Role).filter(Role.name == "user").first()
        if user_role:
            student.roles.append(user_role)
        db.add(student)
        db.commit()
        db.refresh(student)
        uid = student.id

        # === Tạo danh mục ===
        categories_data = [
            # Thu nhập
            {"name": "Tiền bố mẹ gửi", "type": "income"},
            {"name": "Lương part-time", "type": "income"},
            {"name": "Học bổng", "type": "income"},
            # Chi tiêu
            {"name": "Ăn uống", "type": "expense"},
            {"name": "Di chuyển", "type": "expense"},
            {"name": "Học tập", "type": "expense"},
            {"name": "Giải trí", "type": "expense"},
            {"name": "Sinh hoạt", "type": "expense"},
            {"name": "Điện thoại & Internet", "type": "expense"},
            {"name": "Sức khỏe", "type": "expense"},
            {"name": "Quần áo", "type": "expense"},
            {"name": "Khác", "type": "expense"},
        ]

        cat_map = {}
        for c in categories_data:
            cat = Category(name=c["name"], type=c["type"], user_id=uid)
            db.add(cat)
            db.commit()
            db.refresh(cat)
            cat_map[c["name"]] = cat.id

        # === Tạo giao dịch thực tế của sinh viên (30 ngày) ===
        today = date.today()

        transactions = [
            # --- THU NHẬP ---
            # Đầu tháng: bố mẹ gửi
            {"desc": "Bố mẹ gửi tiền tháng 8", "amount": -5000000, "cat": "Tiền bố mẹ gửi", "days_ago": 28},
            # Giữa tháng: lương part-time
            {"desc": "Lương phụ quán cà phê tuần 1", "amount": -800000, "cat": "Lương part-time", "days_ago": 21},
            {"desc": "Lương phụ quán cà phê tuần 2", "amount": -800000, "cat": "Lương part-time", "days_ago": 14},
            {"desc": "Lương phụ quán cà phê tuần 3", "amount": -800000, "cat": "Lương part-time", "days_ago": 7},

            # --- CHI TIÊU: ĂN UỐNG (chiếm nhiều nhất) ---
            {"desc": "Ăn sáng bún bò Huế", "amount": 30000, "cat": "Ăn uống", "days_ago": 28},
            {"desc": "Cơm trưa căn tin trường", "amount": 25000, "cat": "Ăn uống", "days_ago": 28},
            {"desc": "Trà sữa Gong Cha với bạn", "amount": 45000, "cat": "Ăn uống", "days_ago": 27},
            {"desc": "Cơm trưa quán gần trường", "amount": 30000, "cat": "Ăn uống", "days_ago": 26},
            {"desc": "Ăn tối mì gói + trứng", "amount": 15000, "cat": "Ăn uống", "days_ago": 26},
            {"desc": "Bánh mì sáng", "amount": 20000, "cat": "Ăn uống", "days_ago": 25},
            {"desc": "Cơm trưa căn tin", "amount": 25000, "cat": "Ăn uống", "days_ago": 25},
            {"desc": "Cà phê sữa đá buổi chiều", "amount": 18000, "cat": "Ăn uống", "days_ago": 24},
            {"desc": "Ăn phở sáng", "amount": 35000, "cat": "Ăn uống", "days_ago": 23},
            {"desc": "Cơm gà xối mỡ trưa", "amount": 35000, "cat": "Ăn uống", "days_ago": 22},
            {"desc": "Ăn vặt bánh tráng trộn", "amount": 20000, "cat": "Ăn uống", "days_ago": 21},
            {"desc": "Cơm trưa căn tin", "amount": 25000, "cat": "Ăn uống", "days_ago": 20},
            {"desc": "Bún đậu mắm tôm tối", "amount": 40000, "cat": "Ăn uống", "days_ago": 19},
            {"desc": "Bánh mì trứng sáng", "amount": 15000, "cat": "Ăn uống", "days_ago": 18},
            {"desc": "Cơm trưa + nước ngọt", "amount": 32000, "cat": "Ăn uống", "days_ago": 17},
            {"desc": "Cà phê Highland chiều", "amount": 39000, "cat": "Ăn uống", "days_ago": 16},
            {"desc": "Ăn lẩu sinh nhật bạn (chia)", "amount": 120000, "cat": "Ăn uống", "days_ago": 15},
            {"desc": "Xôi sáng", "amount": 15000, "cat": "Ăn uống", "days_ago": 14},
            {"desc": "Cơm văn phòng trưa", "amount": 28000, "cat": "Ăn uống", "days_ago": 13},
            {"desc": "Trà đào cam sả", "amount": 25000, "cat": "Ăn uống", "days_ago": 12},
            {"desc": "Cơm tấm sáng", "amount": 30000, "cat": "Ăn uống", "days_ago": 10},
            {"desc": "Mì Quảng trưa", "amount": 30000, "cat": "Ăn uống", "days_ago": 8},
            {"desc": "Gỏi cuốn + nước mía", "amount": 25000, "cat": "Ăn uống", "days_ago": 6},
            {"desc": "Bánh cuốn sáng nay", "amount": 25000, "cat": "Ăn uống", "days_ago": 4},
            {"desc": "Cơm trưa hôm nay", "amount": 28000, "cat": "Ăn uống", "days_ago": 2},
            {"desc": "Cafe sáng nay", "amount": 20000, "cat": "Ăn uống", "days_ago": 1},
            {"desc": "Cơm trưa nay", "amount": 25000, "cat": "Ăn uống", "days_ago": 0},

            # --- CHI TIÊU: DI CHUYỂN ---
            {"desc": "Đổ xăng xe máy", "amount": 80000, "cat": "Di chuyển", "days_ago": 25},
            {"desc": "Gửi xe ở trường (cả tuần)", "amount": 30000, "cat": "Di chuyển", "days_ago": 20},
            {"desc": "Grab đi học mưa to", "amount": 25000, "cat": "Di chuyển", "days_ago": 16},
            {"desc": "Đổ xăng xe máy lần 2", "amount": 70000, "cat": "Di chuyển", "days_ago": 10},
            {"desc": "Gửi xe ở trường tuần 3", "amount": 30000, "cat": "Di chuyển", "days_ago": 6},

            # --- CHI TIÊU: HỌC TẬP ---
            {"desc": "Mua sách Lập trình Python", "amount": 120000, "cat": "Học tập", "days_ago": 27},
            {"desc": "In tài liệu ôn thi", "amount": 35000, "cat": "Học tập", "days_ago": 18},
            {"desc": "Mua vở + bút bi", "amount": 25000, "cat": "Học tập", "days_ago": 12},
            {"desc": "Photocopy đề cương", "amount": 15000, "cat": "Học tập", "days_ago": 5},

            # --- CHI TIÊU: GIẢI TRÍ ---
            {"desc": "Xem phim CGV cuối tuần", "amount": 75000, "cat": "Giải trí", "days_ago": 22},
            {"desc": "Mua game Steam sale", "amount": 89000, "cat": "Giải trí", "days_ago": 15},
            {"desc": "Bi-a với bạn tối thứ 7", "amount": 40000, "cat": "Giải trí", "days_ago": 8},

            # --- CHI TIÊU: SINH HOẠT ---
            {"desc": "Tiền trọ tháng 8", "amount": 1500000, "cat": "Sinh hoạt", "days_ago": 28},
            {"desc": "Tiền điện nước phòng trọ", "amount": 250000, "cat": "Sinh hoạt", "days_ago": 28},
            {"desc": "Mua dầu gội + sữa tắm", "amount": 85000, "cat": "Sinh hoạt", "days_ago": 20},
            {"desc": "Giặt ủi quần áo", "amount": 40000, "cat": "Sinh hoạt", "days_ago": 14},
            {"desc": "Mua khăn mặt + bàn chải", "amount": 30000, "cat": "Sinh hoạt", "days_ago": 7},

            # --- CHI TIÊU: ĐIỆN THOẠI ---
            {"desc": "Nạp tiền điện thoại", "amount": 50000, "cat": "Điện thoại & Internet", "days_ago": 25},
            {"desc": "Gia hạn gói 4G Viettel", "amount": 77000, "cat": "Điện thoại & Internet", "days_ago": 3},

            # --- CHI TIÊU: SỨC KHỎE ---
            {"desc": "Mua thuốc cảm cúm", "amount": 45000, "cat": "Sức khỏe", "days_ago": 19},

            # --- CHI TIÊU: QUẦN ÁO ---
            {"desc": "Mua áo thun Uniqlo sale", "amount": 199000, "cat": "Quần áo", "days_ago": 11},

            # --- CHI TIÊU: KHÁC ---
            {"desc": "Mừng sinh nhật bạn thân", "amount": 100000, "cat": "Khác", "days_ago": 15},
            {"desc": "Đóng quỹ lớp tháng 8", "amount": 50000, "cat": "Khác", "days_ago": 26},
        ]

        for tx_data in transactions:
            tx = Transaction(
                user_id=uid,
                category_id=cat_map[tx_data["cat"]],
                amount=abs(tx_data["amount"]),
                description=tx_data["desc"],
                transaction_date=today - timedelta(days=tx_data["days_ago"]),
            )
            db.add(tx)

        db.commit()

        # Thống kê
        total_income = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
        total_expense = sum(t["amount"] for t in transactions if t["amount"] > 0)
        print(f"✅ Seed dữ liệu sinh viên thành công!")
        print(f"   👤 Tài khoản: sinhvien / 123456")
        print(f"   📁 Danh mục: {len(categories_data)} danh mục")
        print(f"   📝 Giao dịch: {len(transactions)} giao dịch")
        print(f"   💰 Tổng thu: {total_income:,.0f} ₫")
        print(f"   💸 Tổng chi: {total_expense:,.0f} ₫")
        print(f"   📊 Số dư: {total_income - total_expense:,.0f} ₫")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_student_data()
