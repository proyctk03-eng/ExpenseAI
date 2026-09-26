import os
import sys
import random
from datetime import date, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from src.database import SessionLocal
from src.models import User, Transaction, Category

def seed_data():
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        print("Admin user not found!")
        return

    # Categories
    categories = db.query(Category).all()
    expense_cats = [c for c in categories if c.type == 'expense']
    income_cats = [c for c in categories if c.type == 'income']

    if not expense_cats or not income_cats:
        print("No categories found. Please run initial seed first.")
        return

    expenses_desc = {
        "Ăn uống": ["Ăn trưa", "Ăn tối", "Cà phê", "Mua siêu thị", "Ăn sáng", "Ăn vặt"],
        "Di chuyển": ["Đổ xăng", "Grab/Taxi", "Vé xe bus", "Gửi xe"],
        "Nhà cửa": ["Tiền điện", "Tiền nước", "Tiền mạng", "Tiền rác", "Mua đồ gia dụng"],
        "Cá nhân": ["Cắt tóc", "Mua quần áo", "Mua mỹ phẩm", "Tập gym"],
        "Giải trí": ["Xem phim", "Netflix", "Spotify", "Du lịch", "Mua sách"],
        "Khác": ["Trả nợ", "Đám cưới", "Sinh nhật"]
    }

    incomes_desc = {
        "Lương": ["Lương tháng", "Thưởng dự án", "Lương làm thêm"],
        "Kinh doanh": ["Bán hàng", "Lãi đầu tư", "Cho thuê nhà"],
        "Khác": ["Được tặng", "Tiền hoàn lại"]
    }

    # Fetch existing to avoid duplicates
    existing_txs = set()
    for tx in db.query(Transaction).filter(Transaction.user_id == admin_user.id).all():
        existing_txs.add(f"{tx.transaction_date}_{tx.description}_{tx.amount}")

    today = date.today()
    added_count = 0

    # For the last 180 days
    for day_offset in range(180):
        current_date = today - timedelta(days=day_offset)
        
        # 1-3 expenses per day
        num_expenses = random.randint(1, 3)
        for _ in range(num_expenses):
            cat = random.choice(expense_cats)
            desc_list = expenses_desc.get(cat.name, ["Chi tiêu " + cat.name])
            desc = random.choice(desc_list)
            amount = random.randint(20, 500) * 1000 # 20k to 500k
            
            key = f"{current_date}_{desc}_{amount}"
            if key not in existing_txs:
                tx = Transaction(
                    user_id=admin_user.id,
                    amount=amount,
                    category_id=cat.id,
                    description=desc,
                    transaction_date=current_date
                )
                db.add(tx)
                existing_txs.add(key)
                added_count += 1

        # Income: typically once or twice a month, let's say on the 1st or 15th
        if current_date.day in (1, 15):
            cat = random.choice(income_cats)
            desc_list = incomes_desc.get(cat.name, ["Thu nhập " + cat.name])
            desc = random.choice(desc_list)
            amount = random.randint(5000, 20000) * 1000 # 5M to 20M
            
            key = f"{current_date}_{desc}_{amount}"
            if key not in existing_txs:
                tx = Transaction(
                    user_id=admin_user.id,
                    amount=amount,
                    category_id=cat.id,
                    description=desc,
                    transaction_date=current_date
                )
                db.add(tx)
                existing_txs.add(key)
                added_count += 1

    db.commit()
    db.close()
    print(f"Successfully added {added_count} new transactions for the last 6 months without duplicates.")

if __name__ == "__main__":
    seed_data()
