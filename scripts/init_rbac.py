import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.database import SessionLocal, init_db
from src.models.rbac import Role, Permission
from src.models.user import User
from src.utils.security import get_password_hash

def init_rbac():
    init_db()
    db = SessionLocal()
    
    try:
        # Define base permissions
        permissions = [
            {"name": "*:*", "resource": "all", "action": "all"},
            {"name": "transaction:create", "resource": "transaction", "action": "create"},
            {"name": "transaction:read", "resource": "transaction", "action": "read"},
            {"name": "transaction:update", "resource": "transaction", "action": "update"},
            {"name": "transaction:delete", "resource": "transaction", "action": "delete"},
            {"name": "category:create", "resource": "category", "action": "create"},
            {"name": "category:read", "resource": "category", "action": "read"},
            {"name": "category:update", "resource": "category", "action": "update"},
            {"name": "category:delete", "resource": "category", "action": "delete"},
            {"name": "report:read", "resource": "report", "action": "read"}
        ]
        
        perm_objs = {}
        for p_data in permissions:
            perm = db.query(Permission).filter(Permission.name == p_data["name"]).first()
            if not perm:
                perm = Permission(**p_data)
                db.add(perm)
                db.commit()
                db.refresh(perm)
            perm_objs[p_data["name"]] = perm
            
        # Define roles
        roles = [
            {
                "name": "admin", 
                "description": "Toàn quyền hệ thống",
                "permissions": ["*:*"]
            },
            {
                "name": "user",
                "description": "Người dùng cơ bản",
                "permissions": [
                    "transaction:create", "transaction:read", "transaction:update", "transaction:delete",
                    "category:create", "category:read", "category:update", "category:delete",
                    "report:read"
                ]
            },
            {
                "name": "viewer",
                "description": "Chỉ xem, không thể sửa đổi",
                "permissions": ["transaction:read", "category:read", "report:read"]
            }
        ]
        
        role_objs = {}
        for r_data in roles:
            role = db.query(Role).filter(Role.name == r_data["name"]).first()
            if not role:
                role = Role(name=r_data["name"], description=r_data["description"])
                db.add(role)
                db.commit()
                db.refresh(role)
            
            # Update permissions for role
            role.permissions = [perm_objs[p] for p in r_data["permissions"]]
            db.commit()
            role_objs[r_data["name"]] = role
            
        # Create default admin user if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@expenseai.com",
                hashed_password=get_password_hash("admin123")
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
        if role_objs["admin"] not in admin_user.roles:
            admin_user.roles.append(role_objs["admin"])
            db.commit()
            
        print("✅ Khởi tạo hệ thống RBAC thành công!")
        print("   Tài khoản Admin mặc định: admin / admin123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi khởi tạo RBAC: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_rbac()
