import os
import sys
from datetime import datetime, time, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import SessionLocal
from src.models.models import ProgrammingGrid

def seed_radio():
    session = SessionLocal()

    print("Clearing existing radio programming grid...")
    session.query(ProgrammingGrid).filter(ProgrammingGrid.media_type == "radio").delete(synchronize_session=False)
    session.commit()

    # 5 Praças / Mercados solicitados
    markets = ["SP", "RJ", "POA", "BH", "BSB"]

    # Emissoras de rádio solicitadas
    radio_stations = [
        "BANDNEWS FM",
        "CBN",
        "JOVEM PAN",
        "RADIO ELDORADO",
        "ALPHA FM",
        "TRANSAMERICA"
    ]

    # Faixas horárias padrão para rádio
    time_blocks = [
        ("06:00:00", "10:00:00", "Prime Time Matutino (Notícias & Trânsito)", "Faixa matutina de alta audiência e boletins em tempo real"),
        ("10:00:00", "14:00:00", "Faixa Almoço & Debates", "Cobertura de acontecimentos do meio-dia, esportes e economia"),
        ("14:00:00", "18:00:00", "Faixa Vespertina & Variedades", "Atualizações diárias, cultura, música e entrevistas"),
        ("18:00:00", "22:00:00", "Pico da Tarde / Volta para Casa", "Resumo das notícias do dia, trânsito e análise esportiva"),
        ("22:00:00", "23:59:59", "Faixa Noturna / Madrugada", "Música, podcasts gravados e síntese do noticiário")
    ]

    start_date = date(2026, 6, 22)
    end_date = date(2026, 6, 28)
    
    total_added = 0
    curr_date = start_date
    while curr_date <= end_date:
        for market in markets:
            for station in radio_stations:
                for s_time_str, e_time_str, block_name, desc in time_blocks:
                    st_h, st_m, st_s = map(int, s_time_str.split(":"))
                    et_h, et_m, et_s = map(int, e_time_str.split(":"))
                    
                    grid_item = ProgrammingGrid(
                        channel=station,
                        broadcast_date=curr_date,
                        start_time=time(st_h, st_m, st_s),
                        end_time=time(et_h, et_m, et_s),
                        program_name=f"{station} - {block_name}",
                        description=f"{desc} na praça {market}.",
                        market=market,
                        media_type="radio"
                    )
                    session.add(grid_item)
                    total_added += 1
                    
        curr_date += timedelta(days=1)

    session.commit()
    print(f"Successfully seeded {total_added} radio grid entries across 5 markets (SP, RJ, POA, BH, BSB)!")
    session.close()

if __name__ == "__main__":
    seed_radio()
