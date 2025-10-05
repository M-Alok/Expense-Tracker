from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

encoded_password = quote_plus(os.getenv('DB_PASSWORD'))

DATABASE_URL = f'mysql+pymysql://expenseuser:{encoded_password}@localhost/expense_tracker'
engine = create_engine(DATABASE_URL)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()