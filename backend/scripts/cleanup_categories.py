import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.models import Category

def cleanup_categories():
    db = SessionLocal()
    
    print("Đang quét danh mục...")
    # 1. Cập nhật is_system = True cho các danh mục mặc định (user_id = None)
    system_cats = db.query(Category).filter(Category.user_id.is_(None)).all()
    for cat in system_cats:
        if not cat.is_system:
            cat.is_system = True
            print(f"Đã cập nhật is_system=True cho: {cat.name}")
    
    # 2. Xóa các danh mục bị trùng lặp (nếu có cùng user_id, cùng name, cùng type)
    all_cats = db.query(Category).all()
    seen = set()
    duplicates_deleted = 0
    
    for cat in all_cats:
        key = (cat.user_id, cat.name, cat.type)
        if key in seen:
            db.delete(cat)
            print(f"Đã xóa danh mục trùng lặp: {cat.name} (user_id: {cat.user_id})")
            duplicates_deleted += 1
        else:
            seen.add(key)
            
    db.commit()
    print(f"Dọn dẹp hoàn tất. Đã xóa {duplicates_deleted} bản ghi trùng lặp.")
    db.close()

if __name__ == "__main__":
    cleanup_categories()
