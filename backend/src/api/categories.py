"""API quản lý danh mục."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Category, User, Transaction
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.utils.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
def get_categories(all_users: bool = False, db: Session = Depends(get_db), current_user: User = Depends(require_permission("category:read"))):
    if all_users and current_user.has_permission("*:*"):
        return db.query(Category).all()
    return db.query(Category).filter((Category.user_id == current_user.id) | (Category.user_id == None)).all()

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("category:create"))):
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category_in.name,
        Category.type == category_in.type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Danh mục đã tồn tại")
        
    new_category = Category(name=category_in.name, type=category_in.type, user_id=current_user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_in: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("category:update"))):
    if current_user.has_permission("*:*"):
        category = db.query(Category).filter(Category.id == category_id).first()
    else:
        category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
        
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    if category.is_system and not current_user.has_permission("*:*"):
        raise HTTPException(status_code=403, detail="Không thể sửa danh mục hệ thống")
        
    if category_in.name is not None: category.name = category_in.name
    if category_in.type is not None: category.type = category_in.type
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("category:delete"))):
    if current_user.has_permission("*:*"):
        category = db.query(Category).filter(Category.id == category_id).first()
    else:
        category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
        
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    if category.is_system and not current_user.has_permission("*:*"):
        raise HTTPException(status_code=403, detail="Không thể xóa danh mục hệ thống")
        
    if db.query(Transaction).filter(Transaction.category_id == category.id).first():
        raise HTTPException(status_code=400, detail="Không thể xóa danh mục đang có giao dịch")
        
    db.delete(category)
    db.commit()
