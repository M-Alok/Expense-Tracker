from .database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    
    categories = relationship('Category', back_populates='owner')
    
    expenses = relationship('Expense', back_populates='owner')

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))

    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='categories')

    expenses = relationship('Expense', back_populates='category')

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    description = Column(String(200))
    date = Column(DateTime, default=datetime.utcnow)
    type = Column(String(20)) # expense or income

    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='expenses')

    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="expenses")