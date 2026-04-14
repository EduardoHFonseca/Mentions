import sys
import os

# Adiciona o diretório raiz ao path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import admin_engine, Base
from src.models.models import User, MonitoringSet, MonitoringRule, ProgrammingGrid, SystemConfig, Mention

def init_db():
    print("Iniciando a criação das tabelas no PostgreSQL (como Admin)...")
    try:
        Base.metadata.create_all(bind=admin_engine)
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    init_db()
