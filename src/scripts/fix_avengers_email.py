from src.database import SessionLocal
from src.models import models

db = SessionLocal()
user = db.query(models.User).filter(models.User.company_name == "Avengers do MKT").first()
if user:
    user.email = user.email.lower()
    db.commit()
    print(f"Email for {user.company_name} updated to {user.email}")
else:
    print("User not found")
db.close()
