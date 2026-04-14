import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import SessionLocal
from src.models import models

def seed_specific_users():
    db = SessionLocal()
    try:
        # Define users to create
        users_data = [
            {"email": "admin@mentions.com", "full_name": "Admin", "role": "admin", "company_name": "Kantar"},
            {"email": "operator@mentions.com", "full_name": "Operator", "role": "operator", "company_name": "Kantar"},
            {"email": "client@mentions.com", "full_name": "Client", "role": "client", "company_name": "Empresa Cliente"}
        ]

        for data in users_data:
            user = db.query(models.User).filter(models.User.email == data["email"]).first()
            if not user:
                print(f"Creating user: {data['full_name']}...")
                user = models.User(
                    email=data["email"],
                    password_hash="1234",  # In a real app, use bcrypt. For now, matching user request.
                    full_name=data["full_name"],
                    role=data["role"],
                    company_name=data["company_name"],
                    status="approved"
                )
                db.add(user)
            else:
                print(f"User {data['full_name']} already exists, updating password.")
                user.password_hash = "1234"
        
        db.commit()
        print("Users seeded successfully!")
    except Exception as e:
        print(f"Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_specific_users()
