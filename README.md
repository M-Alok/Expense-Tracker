Description: A personal finance/expense tracker where users can log daily expenses and incomes, categorize them, and generate monthly/weekly reports as downloadable PDFs.

React: [Expense Tracker](https://expense-tracker-eight-ivory-76.vercel.app/)
FastAPI: [Expensee Tracker API](https://expense-tracker-dah0.onrender.com/docs)

Frontend (React + Tailwind CSS):
1. Login and register forms to authenticate users
2. Dashboard to maintain and vizualize the expenditures
3. Forms to add/view expenses with categories.
4. Charts (using Recharts) for category-wise spending.
5. Downloadable PDF report.

Backend (FastAPI + PostgresSQL + SQLAlchemy):
1. User authentication (JWT-based).
2. CRUD APIs for expenses & categories.
3. API to generate PDF expense report using reportlab.
