import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

# Đảm bảo có thể import module từ thư mục gốc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.models import Transaction

def cleanup_duplicate_transactions():
    db = SessionLocal()
    
    print("Đang quét toàn bộ giao dịch...")
    txs = db.query(Transaction).order_by(Transaction.id.asc()).all()
    
    seen = set()
    deleted_count = 0
    
    for tx in txs:
        # Gom nhóm theo (description, amount, date)
        # Bất kể user_id nào, nếu giống nhau sẽ xóa (giữ id nhỏ nhất vì đã order asc)
        key = (tx.description.strip().lower(), tx.amount, tx.transaction_date)
        
        if key in seen:
            db.delete(tx)
            deleted_count += 1
        else:
            seen.add(key)
            
    db.commit()
    print(f"Dọn dẹp hoàn tất. Đã xóa {deleted_count} giao dịch bị trùng lặp.")
    db.close()

if __name__ == "__main__":
    cleanup_duplicate_transactions()
