from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from sqlalchemy import func
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
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
    else:
        start_date = now - timedelta(days=30)
    
    # Get expenses of current user
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date
    ).all()
    
    # Generate PDF with margins
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title
    title = Paragraph(f"Expense Report", title_style)
    elements.append(title)
    
    subtitle = Paragraph(
        f"{period.capitalize()} Report | {start_date.strftime('%B %d, %Y')} - {now.strftime('%B %d, %Y')}", 
        subtitle_style
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Calculate totals
    total_income = sum(e.amount for e in expenses if e.type == "income")
    total_expense = sum(e.amount for e in expenses if e.type == "expense")
    balance = total_income - total_expense
    
    # Summary cards in table format
    summary_data = [
        ['Total Income', 'Total Expenses', 'Balance'],
        [f"Rs. {total_income:.2f}", f"Rs. {total_expense:.2f}", f"Rs. {balance:.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 12),

        # Data row
        ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#e8f5e9')),
        ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#ffebee')),
        ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#e3f2fd') if balance >= 0 else colors.HexColor('#ffcdd2')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('TEXTCOLOR', (0, 1), (0, 1), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#c62828')),
        ('TEXTCOLOR', (2, 1), (2, 1), colors.HexColor('#1565c0') if balance >= 0 else colors.HexColor('#c62828')),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 8),

        # Borders
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#3498db')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 25))
    
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
        elements.append(Paragraph("Category Breakdown", heading_style))
        cat_table_data = [['Category', 'Amount', 'Percentage']]
        
        for cat_name, total in category_data:
            percentage = (total / total_expense * 100) if total_expense > 0 else 0
            cat_table_data.append([cat_name, f"Rs. {total:.2f}", f"{percentage:.1f}%"])
        
        cat_table = Table(cat_table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        cat_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 10),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            
            # Borders
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 25))
    
    # Transactions table
    elements.append(Paragraph("Recent Transactions", heading_style))
    table_data = [['Date', 'Description', 'Category', 'Type', 'Amount']]
    
    for expense in expenses:
        table_data.append([
            expense.date.strftime('%d %b %Y'),
            expense.description[:28] + '...' if len(expense.description) > 28 else expense.description,
            expense.category.name,
            expense.type.capitalize(),
            f"Rs. {expense.amount:.2f}"
        ])
    
    table = Table(table_data, colWidths=[1*inch, 2.2*inch, 1.3*inch, 0.8*inch, 1*inch])
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (2, -1), 'LEFT'),
        ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
        
        # Data rows
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        
        # Borders
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
    ]))
    elements.append(table)
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER
    )
    footer = Paragraph(f"Generated on {now.strftime('%B %d, %Y at %I:%M %p')}", footer_style)
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=expense_report_{period}.pdf"}
    )