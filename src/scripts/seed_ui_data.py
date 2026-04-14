import sys
import os
import uuid
from datetime import datetime, timedelta, date

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import SessionLocal
from src.models import models

def seed_reports_and_invoices():
    db = SessionLocal()
    try:
        # Get the first client
        user = db.query(models.User).filter(models.User.role == "client").first()
        if not user:
            print("No client found. Creating a default client...")
            user = models.User(
                email="client@mentions.com",
                password_hash="fakehash",
                full_name="Cliente Exemplo",
                company_name="Empresa Teste",
                role="client",
                status="approved"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Get the first monitoring set
        m_set = db.query(models.MonitoringSet).filter(models.MonitoringSet.user_id == user.id).first()
        if not m_set:
            print("No monitoring set found for the client. Creating one...")
            m_set = models.MonitoringSet(
                user_id=user.id,
                name="Monitoramento Global ESPN",
                search_terms=["ESPN", "Futebol"],
                status="active"
            )
            db.add(m_set)
            db.commit()
            db.refresh(m_set)

        # Create dummy reports
        print("Creating dummy reports...")
        for i in range(5):
            gen_date = datetime.utcnow() - timedelta(days=i*7)
            report = models.Report(
                user_id=user.id,
                monitoring_set_id=m_set.id,
                generated_at=gen_date,
                file_url=f"https://example.com/reports/report_{i}.pdf",
                period_start=gen_date - timedelta(days=7),
                period_end=gen_date,
                status="ready"
            )
            db.add(report)

        # Create dummy invoices
        print("Creating dummy invoices...")
        for i in range(3):
            due_date = date.today().replace(day=10) - timedelta(days=i*30)
            invoice = models.Invoice(
                user_id=user.id,
                amount=15000 + (i * 1000), # 150.00, 160.00, etc
                due_date=due_date,
                status="paid" if i > 0 else "pending",
                pdf_url=f"https://example.com/invoices/inv_{i}.pdf",
                billing_period=f"2026-0{4-i}"
            )
            db.add(invoice)

        db.commit()
        print("Seed completed successfully!")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_reports_and_invoices()
