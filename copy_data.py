import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from src.database import SessionLocal
from src.models import User, Transaction

def fix():
    db = SessionLocal()
    # Copy transactions from admin (1) to sinhvien (2) if sinhvien has no tx
    sinhvien_count = db.query(Transaction).filter(Transaction.user_id == 2).count()
    if sinhvien_count == 0:
        admin_txs = db.query(Transaction).filter(Transaction.user_id == 1).all()
        for tx in admin_txs:
            new_tx = Transaction(
                user_id=2,
                amount=tx.amount,
                category_id=tx.category_id,
                description=tx.description,
                transaction_date=tx.transaction_date,
                created_at=tx.created_at
            )
            db.add(new_tx)
        db.commit()
        print(f"Successfully copied {len(admin_txs)} transactions to sinhvien account.")
    else:
        print("Sinhvien already has transactions.")

if __name__ == '__main__':
    fix()
