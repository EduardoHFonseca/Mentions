import os
import sys
from datetime import datetime, time, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import ADMIN_DATABASE_URL
from src.models.models import ProgrammingGrid

def seed_grid():
    engine = create_engine(ADMIN_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Clear existing programming grid
    print("Clearing existing programming grid...")
    session.query(ProgrammingGrid).delete()
    session.commit()

    # Date range: Monday June 22, 2026 to Sunday June 28, 2026
    start_date = date(2026, 6, 22)
    
    # Let's define the weekly schedule for each channel
    schedule_data = {
        "GLOBO": {
            "weekday": [
                ("08:00:00", "08:30:00", "Bom Dia Brasil"),
                ("08:30:00", "09:30:00", "Bom Dia Brasil (Cont.)"),
                ("09:30:00", "10:35:00", "Encontro com Patrícia Poeta"),
                ("10:35:00", "11:45:00", "Mais Você"),
                ("11:45:00", "13:00:00", "Praça TV 1ª Edição"),
                ("13:00:00", "13:25:00", "Globo Esporte"),
                ("13:25:00", "14:45:00", "Jornal Hoje"),
                ("14:45:00", "15:30:00", "Edição Especial: Mulheres de Areia"),
                ("15:30:00", "17:05:00", "Sessão da Tarde"),
                ("17:05:00", "18:00:00", "Vale a Pena Ver de Novo: Senhora do Destino"),
                ("18:00:00", "19:15:00", "Novela das Seis: No Rancho Fundo"),
                ("19:15:00", "20:30:00", "Novela das Sete: Família é Tudo"),
                ("20:30:00", "21:20:00", "Jornal Nacional"),
                ("21:20:00", "22:25:00", "Novela das Nove: Mania de Você"),
                ("22:25:00", "23:00:00", "Big Brother Brasil (BBB)")
            ],
            "saturday": [
                ("08:00:00", "09:00:00", "Como Será?"),
                ("09:00:00", "11:45:00", "É de Casa"),
                ("11:45:00", "13:00:00", "Praça TV 1ª Edição"),
                ("13:00:00", "13:25:00", "Globo Esporte"),
                ("13:25:00", "14:10:00", "Jornal Hoje"),
                ("14:10:00", "15:45:00", "Caldeirão com Mion"),
                ("15:45:00", "18:30:00", "Sessão de Sábado"),
                ("18:30:00", "19:15:00", "Novela das Seis: No Rancho Fundo"),
                ("19:15:00", "20:30:00", "Novela das Sete: Família é Tudo"),
                ("20:30:00", "21:20:00", "Jornal Nacional"),
                ("21:20:00", "22:25:00", "Novela das Nove: Mania de Você"),
                ("22:25:00", "23:00:00", "Altas Horas")
            ],
            "sunday": [
                ("08:00:00", "09:00:00", "Globo Comunidade"),
                ("09:00:00", "10:00:00", "Pequenas Empresas & Grandes Negócios"),
                ("10:00:00", "10:30:00", "Globo Rural"),
                ("10:30:00", "12:30:00", "Esporte Espetacular"),
                ("12:30:00", "14:30:00", "Temperatura Máxima"),
                ("14:30:00", "15:45:00", "The Voice Kids"),
                ("15:45:00", "18:00:00", "Futebol na Globo"),
                ("18:00:00", "20:30:00", "Domingão com Huck"),
                ("20:30:00", "23:00:00", "Fantástico")
            ]
        },
        "SBT": {
            "weekday": [
                ("08:00:00", "09:30:00", "Primeiro Impacto"),
                ("09:30:00", "11:15:00", "Chega Mais"),
                ("11:15:00", "13:30:00", "Chega Mais Notícias"),
                ("13:30:00", "14:30:00", "Carinha de Anjo (Reprise)"),
                ("14:30:00", "16:15:00", "Fofocalizando"),
                ("16:15:00", "17:30:00", "Tá na Hora"),
                ("17:30:00", "19:45:00", "Novelas da Tarde: Meu Caminho é Te Amar"),
                ("19:45:00", "20:30:00", "SBT Brasil"),
                ("20:30:00", "21:15:00", "A Caverna das Garotas"),
                ("21:15:00", "22:00:00", "As Aventuras de Poliana (Reprise)"),
                ("22:00:00", "23:00:00", "Programa do Ratinho")
            ],
            "saturday": [
                ("08:00:00", "11:15:00", "Sábado Animado"),
                ("11:15:00", "12:00:00", "Lucas Toon"),
                ("12:00:00", "14:15:00", "Programa Raul Gil"),
                ("14:15:00", "16:00:00", "Cinema em Casa"),
                ("16:00:00", "18:00:00", "Circo do Tiru"),
                ("18:00:00", "19:45:00", "Tá na Hora Sábado"),
                ("19:45:00", "20:30:00", "SBT Brasil"),
                ("20:30:00", "22:15:00", "Esquadrão da Moda"),
                ("22:15:00", "23:00:00", "Sabadou com Virginia")
            ],
            "sunday": [
                ("08:00:00", "09:00:00", "SBT Agro"),
                ("09:00:00", "11:00:00", "Notícias Impressionantes"),
                ("11:00:00", "11:15:00", "Sorteio da Tele Sena"),
                ("11:15:00", "13:30:00", "Domingo Legal: Parte 1"),
                ("13:30:00", "18:15:00", "Domingo Legal: Parte 2"),
                ("18:15:00", "23:00:00", "Programa Silvio Santos com Patrícia Abravanel")
            ]
        },
        "RECORD": {
            "weekday": [
                ("08:00:00", "08:40:00", "Balanço Geral Manhã"),
                ("08:40:00", "10:00:00", "Fala Brasil"),
                ("10:00:00", "11:50:00", "Hoje em Dia"),
                ("11:50:00", "15:30:00", "Balanço Geral SP"),
                ("15:30:00", "16:30:00", "Novela: Apocalipse"),
                ("16:30:00", "17:30:00", "Novela: Gênesis"),
                ("17:30:00", "19:45:00", "Cidade Alerta"),
                ("19:45:00", "20:30:00", "Jornal da Record"),
                ("20:30:00", "21:45:00", "Novela Bíblica: Reis"),
                ("21:45:00", "22:45:00", "Patrulha das Fronteiras"),
                ("22:45:00", "23:00:00", "Jornal da Record News")
            ],
            "saturday": [
                ("08:00:00", "10:00:00", "Fala Brasil Especial"),
                ("10:00:00", "12:00:00", "Escola do Amor"),
                ("12:00:00", "15:00:00", "Balanço Geral Especial"),
                ("15:00:00", "17:00:00", "Cine Aventura"),
                ("17:00:00", "19:45:00", "Cidade Alerta Sábado"),
                ("19:45:00", "20:30:00", "Jornal da Record"),
                ("20:30:00", "22:30:00", "Reis - Melhores Momentos"),
                ("22:30:00", "23:00:00", "Super Tela")
            ],
            "sunday": [
                ("08:00:00", "09:00:00", "Desenhos Bíblicos"),
                ("09:00:00", "12:15:00", "Todo Mundo Odeia o Chris"),
                ("12:15:00", "14:15:00", "Cine Maior"),
                ("14:15:00", "18:00:00", "Hora do Faro"),
                ("18:00:00", "19:45:00", "Acerte ou Caia"),
                ("19:45:00", "23:00:00", "Domingo Espetacular")
            ]
        },
        "REDETV": {
            "weekday": [
                ("08:00:00", "09:00:00", "Manhã do Ronnie"),
                ("09:00:00", "11:30:00", "Vou Te Contar"),
                ("11:30:00", "12:30:00", "Igreja da Graça"),
                ("12:30:00", "15:00:00", "A Tarde É Sua com Sônia Abrão"),
                ("15:00:00", "17:00:00", "Igreja Universal"),
                ("17:00:00", "18:00:00", "Hora de Ação"),
                ("18:00:00", "19:30:00", "RedeTV! News"),
                ("19:30:00", "20:30:00", "Show da Fé"),
                ("20:30:00", "21:30:00", "TV Fama"),
                ("21:30:00", "22:30:00", "Superpop"),
                ("22:30:00", "23:00:00", "Leitura Dinâmica")
            ],
            "saturday": [
                ("08:00:00", "10:00:00", "Ultrafarma Show"),
                ("10:00:00", "12:00:00", "Programa do Jacaré"),
                ("12:00:00", "14:00:00", "Ritmo Brasil"),
                ("14:00:00", "16:00:00", "Auto Mais"),
                ("16:00:00", "18:00:00", "Campeonato Turco"),
                ("18:00:00", "19:30:00", "RedeTV! News"),
                ("19:30:00", "20:30:00", "Show da Fé"),
                ("20:30:00", "22:00:00", "Operação de Risco"),
                ("22:00:00", "23:00:00", "O Céu É o Limite")
            ],
            "sunday": [
                ("08:00:00", "10:00:00", "Ultrafarma Especial"),
                ("10:00:00", "12:00:00", "Cheiro de Galpão"),
                ("12:00:00", "14:00:00", "João Kleber Show (Reprise)"),
                ("14:00:00", "18:00:00", "Geral do Povo com Geraldo Luís"),
                ("18:00:00", "19:30:00", "Hora do Zap"),
                ("19:30:00", "23:00:00", "João Kleber Show")
            ]
        },
        "BANDEIRANTES": {
            "weekday": [
                ("08:00:00", "09:00:00", "Bora Brasil"),
                ("09:00:00", "11:00:00", "The Chef com Edu Guedes"),
                ("11:00:00", "13:00:00", "Jogo Aberto"),
                ("13:00:00", "14:30:00", "Os Donos da Bola"),
                ("14:30:00", "16:00:00", "Melhor da Tarde com Catia Fonseca"),
                ("16:00:00", "19:20:00", "Brasil Urgente com Datena"),
                ("19:20:00", "20:30:00", "Jornal da Band"),
                ("20:30:00", "21:20:00", "Melhor da Noite"),
                ("21:20:00", "22:00:00", "Perrengue do Dia"),
                ("22:00:00", "23:00:00", "MasterChef Brasil")
            ],
            "saturday": [
                ("08:00:00", "10:00:00", "Band Kids"),
                ("10:00:00", "12:00:00", "Nosso Agro"),
                ("12:00:00", "13:00:00", "Esporte Total Sábado"),
                ("13:00:00", "16:00:00", "Band Esporte Clube"),
                ("16:00:00", "19:20:00", "Brasil Urgente Sábado"),
                ("19:20:00", "20:30:00", "Jornal da Band"),
                ("20:30:00", "22:00:00", "Documentários Band"),
                ("22:00:00", "23:00:00", "UFC na Band")
            ],
            "sunday": [
                ("08:00:00", "09:00:00", "Pé na Estrada"),
                ("09:00:00", "10:30:00", "Band Motores"),
                ("10:30:00", "12:00:00", "Show do Esporte (Aquecimento)"),
                ("12:00:00", "18:00:00", "Show do Esporte"),
                ("18:00:00", "20:00:00", "Apito Final com Neto"),
                ("20:00:00", "22:30:00", "Perrengue na Band"),
                ("22:30:00", "23:00:00", "Canal Livre")
            ]
        }
    }

    records_to_add = []
    
    # Loop over 7 days (Monday June 22 to Sunday June 28)
    for day_offset in range(7):
        current_date = start_date + timedelta(days=day_offset)
        # Weekday: Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
        weekday_num = current_date.weekday() 
        
        if weekday_num < 5:
            day_type = "weekday"
        elif weekday_num == 5:
            day_type = "saturday"
        else:
            day_type = "sunday"

        for channel, day_schedules in schedule_data.items():
            programs = day_schedules[day_type]
            for start_str, end_str, prog_name in programs:
                s_time = datetime.strptime(start_str, "%H:%M:%S").time()
                e_time = datetime.strptime(end_str, "%H:%M:%S").time() if end_str else None
                
                grid_entry = ProgrammingGrid(
                    channel=channel,
                    broadcast_date=current_date,
                    start_time=s_time,
                    end_time=e_time,
                    program_name=prog_name,
                    description=f"Exibição real de {prog_name} na rede {channel}.",
                    is_live=False
                )
                records_to_add.append(grid_entry)

    if records_to_add:
        session.bulk_save_objects(records_to_add)
        session.commit()
        print(f"Successfully seeded {len(records_to_add)} slots of real programming grid!")
    else:
        print("No records created.")

    session.close()

if __name__ == "__main__":
    seed_grid()
