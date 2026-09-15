"""
Thiết lập kết nối cơ sở dữ liệu sử dụng SQLAlchemy 2.0.
"""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from src.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_default_rbac(db: Session) -> None:
    from src.models.rbac import Role, Permission
    permissions_data = [
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
    perm_map = {}
    for p_data in permissions_data:
        p = db.query(Permission).filter(Permission.name == p_data["name"]).first()
        if not p:
            p = Permission(**p_data)
            db.add(p)
            db.flush()
        perm_map[p_data["name"]] = p

    roles_data = [
        {"name": "admin", "description": "Toàn quyền hệ thống", "perms": ["*:*"]},
        {"name": "user", "description": "Người dùng cơ bản", "perms": [
            "transaction:create", "transaction:read", "transaction:update", "transaction:delete",
            "category:create", "category:read", "category:update", "category:delete", "report:read"
        ]},
        {"name": "viewer", "description": "Chỉ xem", "perms": ["transaction:read", "category:read", "report:read"]}
    ]
    for r_data in roles_data:
        r = db.query(Role).filter(Role.name == r_data["name"]).first()
        if not r:
            r = Role(name=r_data["name"], description=r_data["description"])
            db.add(r)
            db.flush()
        r.permissions = [perm_map[p_name] for p_name in r_data["perms"] if p_name in perm_map]
    db.commit()

def seed_default_categories(db: Session) -> None:
    from src.models import Category
    
    # Kiểm tra xem đã có danh mục hệ thống nào chưa để tránh vòng lặp thừa
    if not db.query(Category).filter(Category.user_id.is_(None)).first():
        default_categories = [
            {"name": "Lương", "type": "income"},
            {"name": "Thưởng", "type": "income"},
            {"name": "Thu nhập khác", "type": "income"},
            {"name": "Ăn uống", "type": "expense"},
            {"name": "Di chuyển", "type": "expense"},
            {"name": "Học tập", "type": "expense"},
            {"name": "Giải trí", "type": "expense"},
            {"name": "Sinh hoạt", "type": "expense"},
            {"name": "Mua sắm", "type": "expense"},
            {"name": "Khác", "type": "expense"},
        ]
        for cat in default_categories:
            db.add(Category(name=cat["name"], type=cat["type"], user_id=None, is_system=True))
        db.commit()

def seed_default_feedback(db: Session) -> None:
    """Tự động khởi tạo dữ liệu mẫu cho hệ thống Phản hồi (Feedback Tickets)."""
    from datetime import datetime, timedelta, timezone
    from src.models import FeedbackTicket, TicketReply, User
    from src.models.rbac import Role
    from src.utils.security import get_password_hash

    # 1. Đảm bảo role admin và user tồn tại
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    user_role = db.query(Role).filter(Role.name == "user").first()

    # 2. Đảm bảo tài khoản Quản trị viên (admin / admin123)
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@expenseai.com",
            hashed_password=get_password_hash("admin123")
        )
        db.add(admin)
        db.flush()
    elif admin.email.endswith(".local"):
        admin.email = "admin@expenseai.com"
        db.flush()
    if admin_role and admin_role not in admin.roles:
        admin.roles.append(admin_role)

    # 3. Đảm bảo tài khoản Sinh viên (sinhvien / 123456)
    sinhvien = db.query(User).filter(User.username == "sinhvien").first()
    if not sinhvien:
        sinhvien = User(
            username="sinhvien",
            email="sinhvien@university.edu.vn",
            hashed_password=get_password_hash("123456")
        )
        db.add(sinhvien)
        db.flush()
    if admin_role and admin_role in sinhvien.roles:
        sinhvien.roles.remove(admin_role)
    if user_role and user_role not in sinhvien.roles:
        sinhvien.roles.append(user_role)

    # 4. Đảm bảo người dùng mẫu khác
    other_users_data = [
        {"username": "tran_thi_bich", "email": "bich.tran@yahoo.com"},
        {"username": "le_hoang_nam", "email": "nam.le@fpt.edu.vn"},
        {"username": "vu_mai_anh", "email": "maianh.vu@gmail.com"},
    ]
    other_users = {}
    for u_data in other_users_data:
        u = db.query(User).filter(User.username == u_data["username"]).first()
        if not u:
            u = User(
                username=u_data["username"],
                email=u_data["email"],
                hashed_password=get_password_hash("123456")
            )
            if user_role:
                u.roles.append(user_role)
            db.add(u)
            db.flush()
        other_users[u_data["username"]] = u

    # 5. Nếu chưa có feedback tickets nào, tự động seed 6 phản hồi mẫu
    if db.query(FeedbackTicket).count() == 0:
        now = datetime.now(timezone.utc)
        sample_tickets = [
            {
                "user": sinhvien,
                "subject": "Không xuất được báo cáo chi tiêu dạng PDF trên di động",
                "message": "Em sử dụng trình duyệt Safari trên iPhone 14 Pro, khi bấm nút 'Tải PDF' trong mục Báo cáo thì màn hình load mãi không xong và không tải về tệp tin được. Nhờ ban quản trị kiểm tra giúp em ạ.",
                "topic": "bug",
                "status": "pending",
                "created_at": now - timedelta(hours=2, minutes=15),
                "replies": []
            },
            {
                "user": sinhvien,
                "subject": "Đề xuất thêm tính năng quét hóa đơn bằng OCR camera",
                "message": "Chào ban quản trị, ứng dụng ExpenseAI hiện tại rất mượt mà. Tuy nhiên sẽ rất tiện lợi nếu có thêm tính năng chụp ảnh hóa đơn mua sắm/cà phê rồi AI tự động nhận diện số tiền và phân loại thay vì phải gõ tay. Hy vọng tính năng này sớm được đưa vào hệ thống!",
                "topic": "feature",
                "status": "in_progress",
                "created_at": now - timedelta(days=1, hours=5),
                "replies": [
                    {
                        "user": admin,
                        "message": "Chào bạn, cảm ơn ý kiến đóng góp rất giá trị! Đội ngũ kỹ thuật ExpenseAI hiện đang nghiên cứu tích hợp mô hình thị giác máy tính OCR với Google Gemini Vision để hỗ trợ quét hóa đơn. Tính năng này dự kiến sẽ ra mắt trong bản cập nhật tới.",
                        "created_at": now - timedelta(hours=18)
                    },
                    {
                        "user": sinhvien,
                        "message": "Tuyệt vời quá! Rất mong chờ bản cập nhật tiếp theo của hệ thống. Cảm ơn admin hỗ trợ nhanh ạ!",
                        "created_at": now - timedelta(hours=14)
                    }
                ]
            },
            {
                "user": sinhvien,
                "subject": "Lỗi phân loại nhầm tiền thưởng thành chi phí khác",
                "message": "Hôm qua em nhập mô tả 'Thưởng dự án quý 3' với số tiền 5.000.000đ nhưng AI lại gợi ý danh mục chi phí khác thay vì Thu nhập / Thưởng. Nhờ admin kiểm tra lại prompt phân loại giúp em.",
                "topic": "bug",
                "status": "resolved",
                "created_at": now - timedelta(days=2, hours=3),
                "replies": [
                    {
                        "user": admin,
                        "message": "Chào bạn, chúng tôi đã cập nhật lại bộ quy tắc Prompt Rule của AI phân loại thu chi, đồng thời bổ sung từ khóa 'Thưởng dự án' vào danh mục Thu nhập. Bạn vui lòng thử nhập lại nhé.",
                        "created_at": now - timedelta(days=1, hours=20)
                    },
                    {
                        "user": sinhvien,
                        "message": "Dạ em vừa thử lại và hệ thống đã nhận diện chính xác thành danh mục Thưởng rồi. Cảm ơn admin nhiều!",
                        "created_at": now - timedelta(days=1, hours=10)
                    }
                ]
            },
            {
                "user": other_users["tran_thi_bich"],
                "subject": "Khiếu nại về tốc độ phản hồi của AI tư vấn vào giờ cao điểm",
                "message": "Khoảng 20h tối qua tôi bấm 'Xin lời khuyên chi tiêu từ AI' thì mất hơn 30 giây mới nhận được phản hồi. Tốc độ này hơi chậm so với bình thường.",
                "topic": "complaint",
                "status": "in_progress",
                "created_at": now - timedelta(days=3),
                "replies": [
                    {
                        "user": admin,
                        "message": "Chào bạn Bích, vào khung giờ 20h-21h hàng ngày lưu lượng truy cập hệ thống tăng cao dẫn đến thời gian chờ API AI tăng lên. Chúng tôi đang tối ưu cơ chế bộ nhớ đệm (Caching) và nâng cấp băng thông máy chủ để cải thiện độ trễ.",
                        "created_at": now - timedelta(days=2, hours=12)
                    }
                ]
            },
            {
                "user": other_users["le_hoang_nam"],
                "subject": "Hỏi về cách sao lưu dữ liệu sang Google Drive hoặc Dropbox",
                "message": "Tôi muốn tự động sao lưu định kỳ dữ liệu giao dịch hàng tháng lên đám mây cá nhân để lưu trữ lâu dài. Hiện tại ExpenseAI đã hỗ trợ liên kết dịch vụ lưu trữ ngoài chưa?",
                "topic": "other",
                "status": "resolved",
                "created_at": now - timedelta(days=5),
                "replies": [
                    {
                        "user": admin,
                        "message": "Chào bạn Nam, hiện tại bạn có thể sử dụng chức năng 'Xuất dữ liệu Excel/CSV' trong mục Cài đặt để lưu trữ tệp tin. Tính năng đồng bộ tự động lên Google Drive đang được lên kế hoạch phát triển.",
                        "created_at": now - timedelta(days=4, hours=18)
                    }
                ]
            },
            {
                "user": other_users["vu_mai_anh"],
                "subject": "Yêu cầu xóa tài khoản và toàn bộ lịch sử chi tiêu",
                "message": "Tôi muốn đóng tài khoản và yêu cầu xóa sạch toàn bộ cơ sở dữ liệu giao dịch cá nhân do không còn nhu cầu sử dụng.",
                "topic": "complaint",
                "status": "rejected",
                "created_at": now - timedelta(days=7),
                "replies": [
                    {
                        "user": admin,
                        "message": "Chào bạn Mai Anh, theo chính sách bảo mật dữ liệu, bạn có thể tự xóa từng giao dịch trong mục 'Quản lý giao dịch'. Yêu cầu xóa vĩnh viễn tài khoản từ hệ thống cần xác thực qua email chính chủ. Vui lòng gửi email từ hộp thư đăng ký để chúng tôi tiến hành thủ tục.",
                        "created_at": now - timedelta(days=6)
                    }
                ]
            }
        ]

        for item in sample_tickets:
            replies_data = item.pop("replies")
            customer_user = item.pop("user")
            ticket = FeedbackTicket(
                user_id=customer_user.id,
                **item
            )
            db.add(ticket)
            db.flush()

            for rep_data in replies_data:
                rep = TicketReply(
                    ticket_id=ticket.id,
                    user_id=rep_data["user"].id,
                    message=rep_data["message"],
                    created_at=rep_data["created_at"]
                )
                db.add(rep)

    db.commit()

def init_db() -> None:
    from src.models import User, Category, Transaction, AIPrediction, UserMemoryRule  # noqa: F401
    from src.models.rbac import Role, Permission, UserRole, RolePermission  # noqa: F401
    from src.models.feedback import FeedbackTicket, TicketReply  # noqa: F401
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        try:
            seed_default_rbac(db)
            seed_default_categories(db)
            seed_default_feedback(db)
        except Exception:
            db.rollback()



