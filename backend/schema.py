from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    amount: float
    description: str
    date: Optional[datetime] = None
    type: str
    category_id: int

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    description: str
    date: datetime
    type: str
    category_id: int
    category: CategoryResponse
    class Config:
        from_attributes = True