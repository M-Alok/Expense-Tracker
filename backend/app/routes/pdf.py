from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models import User
from app.repository.pdf_repo import generate_pdf_report

router = APIRouter(
    tags=['PDF'],
)

@router.get("/expenses/report/pdf")
def generate_pdf(period: str = "monthly", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return generate_pdf_report(period, current_user, db)