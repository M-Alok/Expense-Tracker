from fastapi import HTTPException
from app.models import Expense
from datetime import datetime

def create_user_expense(expense, current_user, db):
    """Create a new expense for the current user."""
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

def get_user_expense(current_user, db):
    """Retrieve all expenses for the current user."""
    return db.query(Expense).filter(Expense.user_id == current_user.id).order_by(Expense.date.desc()).all()

def update_user_expense(expense_id, expense, current_user, db):
    """Update an existing expense for the current user."""
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

def delete_user_expense(expense_id, current_user, db):
    """Delete an expense for the current user."""
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    category_name = expense.category.name if expense.category else "Unknown"
    amount = expense.amount
    db.delete(expense)
    db.commit()
    return {"message": f"Deleted {category_name} expense of ammount {amount}"}