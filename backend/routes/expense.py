from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..schema import ExpenseResponse, ExpenseCreate
from .auth import get_current_user
from ..database import get_db
from ..models import User, Expense

router = APIRouter(
    tags=['Expense'],
)

@router.post("/expenses", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_expense = Expense(
        amount=expense.amount,
        description=expense.description,
        date=expense.date or datetime.utcnow(),
        type=expense.type,
        category_id=expense.category_id,
        user_id=current_user.id
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/expenses", response_model=List[ExpenseResponse])
def get_expenses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Expense).filter(Expense.user_id == current_user.id).order_by(Expense.date.desc()).all()

@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, expense: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db_expense.amount = expense.amount
    db_expense.description = expense.description
    db_expense.date = expense.date or db_expense.date
    db_expense.type = expense.type
    db_expense.category_id = expense.category_id
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": f"Deleted {expense.category} expense of ammount {expense.amount}"}