from fastapi import HTTPException
from app.models import Category

def create_user_category(category, current_user, db):
    new_category = Category(name=category.name, user_id=current_user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def get_user_category(current_user, db):
    return db.query(Category).filter(Category.user_id == current_user.id).all()

def delete_user_category(category_id, current_user, db):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": f"Deleted {category.name} category"}