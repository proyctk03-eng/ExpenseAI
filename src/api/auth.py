"""API cho xác thực người dùng."""
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
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_to_response(user: User) -> dict:
    """Chuyển đổi User ORM thành dict phù hợp UserResponse."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [r.name for r in user.roles],
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
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
    resp.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, samesite="Lax")
    resp.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=7*24*60*60, samesite="Lax")
    return resp

@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        # Also check authorization header or body if needed
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header.split(" ", 1)[1].strip()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập đã hết hạn",
    )
    if not refresh_token:
        raise credentials_exception
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
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

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    resp = JSONResponse(content={
        "message": "Refresh token thành công",
        "access_token": access_token,
        "token_type": "bearer"
    })
    resp.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, samesite="Lax")
    return resp

@router.post("/logout")
def logout():
    resp = JSONResponse(content={"message": "Đăng xuất thành công"})
    resp.delete_cookie("access_token")
    resp.delete_cookie("refresh_token")
    return resp

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
    return {"status": "success", "message": "Đổi mật khẩu thành công"}
