import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import date, timedelta
from src.database import SessionLocal
from src.models import User, Category, Transaction

def main():
    db = SessionLocal()
    
    users = db.query(User).all()
    if not users:
        print("No users found. Please initialize DB first.")
        return

    categories = db.query(Category).all()
    if not categories:
        print("No categories found.")
        return

    income_cats = [c for c in categories if c.type == "income"]
    expense_cats = [c for c in categories if c.type == "expense"]

    today = date.today()
    start_date = today - timedelta(days=180) # about 6 months

    total_added = 0
    for user in users:
        for month_offset in range(6):
            base_date = start_date + timedelta(days=month_offset * 30)
            
            # 1-2 income transactions per month
            for _ in range(random.randint(1, 2)):
                if income_cats:
                    cat = random.choice(income_cats)
                    amount = random.randint(5000000, 20000000)
                    t_date = base_date + timedelta(days=random.randint(0, 28))
                    if t_date > today: t_date = today
                    
                    t = Transaction(
                        user_id=user.id,
                        category_id=cat.id,
                        amount=amount,
                        description=f"Thu nhập {cat.name} tháng {(month_offset+1)}",
                        transaction_date=t_date
                    )
                    db.add(t)
                    total_added += 1

            # 15-40 expense transactions per month
            for _ in range(random.randint(15, 40)):
                if expense_cats:
                    cat = random.choice(expense_cats)
                    amount = random.randint(50000, 2000000)
                    t_date = base_date + timedelta(days=random.randint(0, 28))
                    if t_date > today: t_date = today
                    
                    t = Transaction(
                        user_id=user.id,
                        category_id=cat.id,
                        amount=amount,
                        description=f"Chi tiêu {cat.name}",
                        transaction_date=t_date
                    )
                    db.add(t)
                    total_added += 1
                    
    db.commit()
    print(f"Successfully seeded {total_added} transactions for {len(users)} users.")

if __name__ == "__main__":
    main()
