import sys
import os
import random
from datetime import date, timedelta
from decimal import Decimal

# Đảm bảo có thể import module từ src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

from src.database import SessionLocal
from src.models import Transaction, Category, User

def get_random_date(start_date: date, end_date: date) -> date:
    days_between = (end_date - start_date).days
    random_days = random.randrange(days_between + 1)
    return start_date + timedelta(days=random_days)

def seed_data():
    db = SessionLocal()
    try:
        print("Đang chuẩn bị tạo dữ liệu seed...")
        
        # 1. Tìm user để gán dữ liệu. Ưu tiên user 'admin', nếu không có thì lấy user đầu tiên
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            user = db.query(User).first()
            if not user:
                print("Lỗi: Không tìm thấy bất kỳ user nào trong database để gán giao dịch.")
                return

        print(f"Sẽ gán dữ liệu cho user: {user.username} (ID: {user.id})")

        # 2. Lấy danh mục mặc định để map category_id
        # Thu nhập
        cat_luong = db.query(Category).filter(Category.name == "Lương").first()
        cat_thuong = db.query(Category).filter(Category.name == "Thưởng").first()
        # Chi tiêu
        cat_an_uong = db.query(Category).filter(Category.name == "Ăn uống").first()
        cat_mua_sam = db.query(Category).filter(Category.name == "Mua sắm").first()
        cat_di_chuyen = db.query(Category).filter(Category.name == "Di chuyển").first()
        cat_giai_tri = db.query(Category).filter(Category.name == "Giải trí").first()

        start_date = date(2026, 9, 1)
        end_date = date(2026, 9, 15)

        transactions_to_add = []

        # --- SINH THU NHẬP ---
        # 1-2 khoản thu nhập lớn
        transactions_to_add.append(Transaction(
            user_id=user.id,
            category_id=cat_luong.id if cat_luong else None,
            amount=Decimal(random.randint(10, 20) * 1000000), # 10tr - 20tr
            description="Lương tháng 8",
            transaction_date=date(2026, 9, 5) # Đầu tháng
        ))

        if random.choice([True, False]):
            transactions_to_add.append(Transaction(
                user_id=user.id,
                category_id=cat_thuong.id if cat_thuong else None,
                amount=Decimal(random.randint(2, 5) * 1000000), # 2tr - 5tr
                description="Thưởng dự án",
                transaction_date=date(2026, 9, 10)
            ))

        # --- SINH CHI TIÊU ---
        # Lưu ý: DB thiết kế check constraint amount > 0, 
        # loại thu/chi được xác định bởi category.type ("expense" hoặc "income")
        expense_templates = [
            # (Danh mục, mô tả, min, max)
            (cat_an_uong, ["Ăn phở sáng", "Cà phê Landmark", "Ăn trưa công ty", "Bún bò Huế"], 30000, 100000),
            (cat_mua_sam, ["Mua quần áo Zara", "Đơn hàng Shopee", "Tạp hóa"], 200000, 500000),
            (cat_di_chuyen, ["Đổ xăng", "Grab đi làm", "Sửa xe"], 50000, 150000),
            (cat_giai_tri, ["Xem phim CGV", "Gia hạn Netflix", "Mua sách"], 100000, 300000)
        ]

        num_expenses = random.randint(20, 28)
        for _ in range(num_expenses):
            cat, desc_list, min_amt, max_amt = random.choice(expense_templates)
            amount = round(random.randint(min_amt, max_amt) / 1000) * 1000 # Làm tròn chẵn nghìn
            
            transactions_to_add.append(Transaction(
                user_id=user.id,
                category_id=cat.id if cat else None,
                amount=Decimal(amount),
                description=random.choice(desc_list),
                transaction_date=get_random_date(start_date, end_date)
            ))

        print(f"Đang insert {len(transactions_to_add)} giao dịch vào Database...")
        
        # 3. Bulk insert an toàn
        db.bulk_save_objects(transactions_to_add)
        db.commit()
        
        print("Tạo dữ liệu Seed thành công!")

    except Exception as e:
        db.rollback()
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        db.close()
        print("Đã đóng kết nối Database.")

if __name__ == "__main__":
    seed_data()
