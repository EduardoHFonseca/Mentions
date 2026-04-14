import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# We use the app user for regular operations
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
# We use the admin user for migrations/creating tables
ADMIN_DATABASE_URL = os.getenv("ADMIN_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
admin_engine = create_engine(ADMIN_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
