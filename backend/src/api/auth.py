"""API cho xác thực người dùng."""
import secrets
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.utils.limiter import limiter
from jose import jwt, JWTError
from src.config import SECRET_KEY, ALGORITHM

from src.database import get_db
from src.models import User, Role
from src.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate, PasswordChange
from src.utils.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from src.utils.dependencies import get_current_user
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, ENVIRONMENT

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_to_response(user: User) -> dict:
    """Chuyển đổi User ORM thành dict phù hợp UserResponse."""
    roles = [r.name for r in user.roles]
    if (user.username == "admin" or user.is_admin) and "admin" not in roles:
        roles.append("admin")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": roles,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    # S-FIX H-08: Gộp thông báo lỗi để ngăn ngừa user/email enumeration
    if db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first():
        raise HTTPException(status_code=400, detail="Tài khoản hoặc email đã tồn tại")
    default_role = db.query(Role).filter(Role.name == "user").first()
    if not default_role:
        default_role = Role(name="user", description="Người dùng cơ bản")
        db.add(default_role)
        db.flush()
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    new_user.roles.append(default_role)
        
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return _user_to_response(new_user)

@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, user_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai username hoặc mật khẩu")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    resp = JSONResponse(content={
        "message": "Đăng nhập thành công",
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "user": _user_to_response(user)
    })
    resp.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, samesite="lax", secure=(ENVIRONMENT == "production"))
    resp.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=7*24*60*60, samesite="lax", secure=(ENVIRONMENT == "production"))
    return resp

@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    token_str = request.cookies.get("refresh_token")
    if not token_str:
        # Also check authorization header or body if needed
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token_str = auth_header.split(" ", 1)[1].strip()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập đã hết hạn",
    )
    if not token_str:
        raise credentials_exception
    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    # S-FIX M-01: Refresh Token Rotation — cấp cả access_token mới và refresh_token mới
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=7)
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    resp = JSONResponse(content={
        "message": "Refresh token thành công",
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token,
    })
    resp.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, samesite="lax", secure=(ENVIRONMENT == "production"))
    resp.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, max_age=7*24*60*60, samesite="lax", secure=(ENVIRONMENT == "production"))
    return resp

@router.post("/logout")
def logout():
    resp = JSONResponse(content={"message": "Đăng xuất thành công"})
    resp.delete_cookie("access_token")
    resp.delete_cookie("refresh_token")
    return resp

# S-FIX H-03: Endpoint cung cấp CSRF Token cho client
@router.get("/csrf-token")
def get_csrf_token(request: Request):
    """Cung cấp CSRF token cho frontend Double-Submit cookie pattern."""
    token = request.cookies.get("csrftoken") or secrets.token_hex(32)
    resp = JSONResponse(content={"csrf_token": token})
    resp.set_cookie(
        key="csrftoken",
        value=token,
        httponly=False,
        samesite="lax",
        secure=(ENVIRONMENT == "production"),
        path="/"
    )
    return resp


# --- S-FIX C-01/C-02/C-03: Demo login endpoint (chỉ hoạt động trong dev) ---
DEMO_ACCOUNTS = {
    "student": "sinhvien",
    "admin": "admin",
}

from pydantic import BaseModel as _BaseModel

class DemoLoginRequest(_BaseModel):
    role: str

@router.post("/demo-login")
@limiter.limit("10/minute")
def demo_login(request: Request, body: DemoLoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập nhanh tài khoản mẫu — CHỈ hoạt động khi ENVIRONMENT=development."""
    if ENVIRONMENT != "development":
        raise HTTPException(status_code=403, detail="Demo login chỉ khả dụng trong môi trường development")

    username = DEMO_ACCOUNTS.get(body.role)
    if not username:
        raise HTTPException(status_code=400, detail="Vai trò không hợp lệ. Chọn 'student' hoặc 'admin'")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Tài khoản demo '{username}' chưa được khởi tạo trong DB")

    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(data={"sub": str(user.id)}, expires_delta=timedelta(days=7))

    resp = JSONResponse(content={
        "message": f"Đăng nhập demo ({body.role}) thành công",
        "user": _user_to_response(user)
    })
    resp.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, samesite="lax", secure=False)
    resp.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=7*24*60*60, samesite="lax", secure=False)
    return resp

@router.get("/demo-accounts")
def get_demo_accounts():
    """Trả về danh sách tài khoản demo (không bao gồm password) — chỉ dev mode."""
    if ENVIRONMENT != "development":
        raise HTTPException(status_code=403, detail="Không khả dụng")
    return {"accounts": [
        {"role": "student", "label": "Sinh viên", "icon": "fa-graduation-cap"},
        {"role": "admin", "label": "Quản trị viên", "icon": "fa-user-shield"},
    ]}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return _user_to_response(current_user)

@router.put("/me", response_model=UserResponse)
def update_users_me(user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_in.email is not None:
        if db.query(User).filter(User.email == user_in.email, User.id != current_user.id).first():
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")
        current_user.email = user_in.email
    if user_in.username is not None:
        if db.query(User).filter(User.username == user_in.username, User.id != current_user.id).first():
            raise HTTPException(status_code=400, detail="Username đã được sử dụng")
        current_user.username = user_in.username
    db.commit()
    db.refresh(current_user)
    return _user_to_response(current_user)

@router.put("/password", status_code=status.HTTP_200_OK)
def change_password(pass_in: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(pass_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác")
    current_user.hashed_password = get_password_hash(pass_in.new_password)
    db.commit()
    # S-FIX H-02: Invalidate current session khi đổi mật khẩu
    resp = JSONResponse(content={"status": "success", "message": "Đổi mật khẩu thành công. Vui lòng đăng nhập lại."})
    resp.delete_cookie("access_token")
    resp.delete_cookie("refresh_token")
    return resp
