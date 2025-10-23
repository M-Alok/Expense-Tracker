from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schema import ExpenseResponse, ExpenseCreate
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models import User

from app.repository.expense_repo import create_user_expense, get_user_expense, update_user_expense, delete_user_expense

router = APIRouter(
    tags=['Expense'],
)

@router.post("/expenses", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_user_expense(expense, current_user, db)

@router.get("/expenses", response_model=List[ExpenseResponse])
def get_expenses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_expense(current_user, db)

@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, expense: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user_expense(expense_id, expense, current_user, db)

@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return delete_user_expense(expense_id, current_user, db)