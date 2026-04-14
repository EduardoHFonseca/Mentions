import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import ADMIN_DATABASE_URL
from src.models.models import ProgrammingGrid

def parse_date(date_str):
    if pd.isna(date_str) or not isinstance(date_str, str):
        return None
    try:
        # Tenta remover o dia da semana se existir (ex: 'Fri 1/10/2025')
        if ' ' in date_str:
            clean_date = date_str.split(' ', 1)[1]
        else:
            clean_date = date_str
        return datetime.strptime(clean_date, '%m/%d/%Y').date()
    except Exception:
        return None

def import_csv_files(data_dir):
    engine = create_engine(ADMIN_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    for file_name in csv_files:
        file_path = os.path.join(data_dir, file_name)
        print(f"Limpando e processando: {file_name}...")
        
        try:
            # Lê com tratamentos para linhas malformadas e delimitadores extras
            df = pd.read_csv(file_path, skipinitialspace=True, on_bad_lines='skip', engine='python')
            
            # Padronização de colunas (Ignora case e espaços)
            df.columns = [c.strip() for c in df.columns]
            
            # Mapeamento de colunas possíveis
            col_map = {
                'Network': 'channel',
                'Air Date (BZT)': 'date',
                'Start Time (BZT)': 'start',
                'EP Name': 'name',
                'Comments': 'desc',
                'LTS': 'type'
            }
            
            # Filtra apenas o que conseguimos mapear
            present_cols = [c for c in df.columns if c in col_map]
            df = df[present_cols].rename(columns=col_map)
            
            # Remove linhas onde campos essenciais estão nulos
            df = df.dropna(subset=['channel', 'date', 'start', 'name'])
            
            # Ordenação
            df = df.sort_values(by=['channel', 'date', 'start'])
            
            records_to_add = []
            
            for i in range(len(df)):
                row = df.iloc[i]
                b_date = parse_date(row['date'])
                if not b_date: continue

                try:
                    s_time = datetime.strptime(str(row['start']).strip(), '%H:%M:%S').time()
                except:
                    continue
                
                # Cálculo do end_time
                e_time = None
                if i + 1 < len(df):
                    next_row = df.iloc[i+1]
                    if next_row['channel'] == row['channel'] and next_row['date'] == row['date']:
                        try:
                            e_time = datetime.strptime(str(next_row['start']).strip(), '%H:%M:%S').time()
                        except: pass
                
                if not e_time:
                    full_dt = datetime.combine(datetime.today(), s_time) + timedelta(hours=1)
                    e_time = full_dt.time()

                grid_entry = ProgrammingGrid(
                    channel=row['channel'],
                    broadcast_date=b_date,
                    start_time=s_time,
                    end_time=e_time,
                    program_name=row['name'],
                    description=str(row['desc']) if 'desc' in row and pd.notnull(row['desc']) else "",
                    is_live=(str(row.get('type')) == 'L')
                )
                records_to_add.append(grid_entry)
            
            if records_to_add:
                session.bulk_save_objects(records_to_add)
                session.commit()
                print(f"✓ {len(records_to_add)} programas importados de {file_name}")
            else:
                print(f"! Nenhum dado válido encontrado em {file_name}")

        except Exception as e:
            session.rollback()
            print(f"✘ Erro crítico em {file_name}: {e}")
            
    session.close()

if __name__ == "__main__":
    DATA_PATH = "/home/efonseca/workspace/Projeto Mentions On-Demand/data"
    import_csv_files(DATA_PATH)
