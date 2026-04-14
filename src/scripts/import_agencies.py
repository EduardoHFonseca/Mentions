import sys
import os
import csv
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import SessionLocal
from src.models import models

def import_agencies():
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "agencias_marketing_ficticias.csv"))
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    db = SessionLocal()
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Standardizing keys since they have spaces/Portuguese characters in the CSV header
            # Header: Nome Fantasia,Razão Social,Endereço,Telefone,CNPJ,Nome para Contato,Email de Contato
            
            for row in reader:
                email = row['Email de Contato'].strip()
                company_name = row['Nome Fantasia'].strip()
                full_name = row['Nome para Contato'].strip()
                
                user = db.query(models.User).filter(models.User.email == email).first()
                if not user:
                    print(f"Importing agency: {company_name} ({email})...")
                    user = models.User(
                        email=email,
                        password_hash="1234", # Default password for initial import
                        full_name=full_name,
                        company_name=company_name,
                        role="client",
                        status="approved",
                        billing_info={
                            "razao_social": row['Razão Social'],
                            "endereco": row['Endereço'],
                            "telefone": row['Telefone'],
                            "cnpj": row['CNPJ']
                        }
                    )
                    db.add(user)
                else:
                    print(f"Agency {company_name} already exists, skipping.")
            
        db.commit()
        print("Agencies imported successfully!")
    except Exception as e:
        print(f"Error importing agencies: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_agencies()
