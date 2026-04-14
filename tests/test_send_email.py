import os
import sys

# Adiciona o diretório src ao path para poder importar o serviço de e-mail
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.email_service import email_service

def test_send_hello():
    recipient = "eduardo.fonseca.na@gmail.com"
    subject = "Hello"
    body = "Este é um teste do sistema de busca de vídeos de TV Mentions On-Demand via AgentMail."
    
    print(f"Tentando enviar e-mail para: {recipient}...")
    
    try:
        # Nota: O SDK do AgentMail espera uma chamada para o método de envio. 
        # Baseado na estrutura criada em email_service.py:
        response = email_service.send_notification(
            to=recipient,
            subject=subject,
            text=body
        )
        print("E-mail enviado com sucesso!")
        print(f"Resposta da API: {response}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

if __name__ == "__main__":
    test_send_hello()
