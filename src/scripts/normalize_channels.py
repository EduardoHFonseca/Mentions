import sys
import os

# Add root directory to path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import AdminSessionLocal
from src.models.models import ProgrammingGrid, MonitoringRule
from sqlalchemy import func

def normalize_channels():
    print("Iniciando a normalização dos canais...")
    
    session = AdminSessionLocal()
    try:
        # Update ProgrammingGrid table
        print("Normalizando tabela programming_grid...")
        grid_count = session.query(ProgrammingGrid).update(
            {ProgrammingGrid.channel: func.upper(func.trim(ProgrammingGrid.channel))},
            synchronize_session=False
        )
        print(f"  {grid_count} registros atualizados em programming_grid.")
        
        # Update MonitoringRule table
        print("Normalizando tabela monitoring_rules...")
        rule_count = session.query(MonitoringRule).update(
            {MonitoringRule.channel: func.upper(func.trim(MonitoringRule.channel))},
            synchronize_session=False
        )
        print(f"  {rule_count} registros atualizados em monitoring_rules.")
        
        session.commit()
        print("Normalização concluída com sucesso.")
        
        # Verify ProgrammingGrid
        new_grid_channels = session.query(ProgrammingGrid.channel).distinct().all()
        print(f"Canais únicos no grid após normalização: {[c[0] for c in new_grid_channels]}")
        
    except Exception as e:
        session.rollback()
        print(f"Erro ao normalizar canais: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    normalize_channels()
