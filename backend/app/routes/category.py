from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schema import CategoryResponse, CategoryCreate
from ..repository.auth import get_current_user
from app.database import get_db
from app.models import User
from app.repository.category_repo import create_user_category, get_user_category, delete_user_category

router = APIRouter(
    tags=['Category'],
)

@router.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_user_category(category, current_user, db)

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_category(current_user, db)

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return delete_user_category(category_id, current_user, db)