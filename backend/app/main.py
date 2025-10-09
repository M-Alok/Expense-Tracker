from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from .routes import user, category, expense, pdf
import logging

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {'message': 'Expense Tracker API 🚀'}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(user.router)
app.include_router(category.router)
app.include_router(expense.router)
app.include_router(pdf.router)