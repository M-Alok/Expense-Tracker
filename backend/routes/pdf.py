from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from sqlalchemy import func
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from fastapi.responses import StreamingResponse

from .auth import get_current_user
from ..database import get_db
from ..models import User, Expense, Category

router = APIRouter(
    tags=['PDF'],
)

@router.get("/expenses/report/pdf")
def generate_pdf_report(period: str = "monthly", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Calculate date range
    now = datetime.utcnow()
    if period == "weekly":
        start_date = now - timedelta(days=7)
    else:  # monthly
        start_date = now - timedelta(days=30)
    
    # Query expenses
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date
    ).all()
    
    # Generate PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"<b>Expense Report - {period.capitalize()}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Summary
    total_income = sum(e.amount for e in expenses if e.type == "income")
    total_expense = sum(e.amount for e in expenses if e.type == "expense")
    balance = total_income - total_expense
    
    summary = Paragraph(f"<b>Summary:</b><br/>Total Income: ${total_income:.2f}<br/>Total Expenses: ${total_expense:.2f}<br/>Balance: ${balance:.2f}", styles['Normal'])
    elements.append(summary)
    elements.append(Spacer(1, 12))
    
    # Category breakdown
    category_data = db.query(
        Category.name,
        func.sum(Expense.amount).label('total')
    ).join(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.type == "expense"
    ).group_by(Category.name).all()
    
    if category_data:
        elements.append(Paragraph("<b>Category Breakdown:</b>", styles['Heading2']))
        cat_table_data = [['Category', 'Amount']]
        for cat_name, total in category_data:
            cat_table_data.append([cat_name, f"${total:.2f}"])
        
        cat_table = Table(cat_table_data)
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 12))
    
    # Transactions table
    elements.append(Paragraph("<b>Transactions:</b>", styles['Heading2']))
    table_data = [['Date', 'Description', 'Category', 'Type', 'Amount']]
    
    for expense in expenses:
        table_data.append([
            expense.date.strftime('%Y-%m-%d'),
            expense.description[:30],
            expense.category.name,
            expense.type.capitalize(),
            f"${expense.amount:.2f}"
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=expense_report_{period}.pdf"}
    )