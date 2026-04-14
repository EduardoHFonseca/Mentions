import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import admin_engine, Base
from src.models import models

def reset_db():
    print("Dropping all tables and recreating them...")
    Base.metadata.drop_all(bind=admin_engine)
    Base.metadata.create_all(bind=admin_engine)
    print("Database reset successfully!")

if __name__ == "__main__":
    reset_db()
