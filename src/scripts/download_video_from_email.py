import os
import sys
import requests
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agentmail import AgentMail

def main():
    print("Iniciando a busca pelo e-mail com anexo de vídeo...")
    
    # Load .env variables
    load_dotenv()
    
    api_key = os.getenv("AGENTMAIL_API_KEY")
    inbox_id = os.getenv("AGENTMAIL_INBOX_ID", "menond@agentmail.to")
    
    if not api_key:
        print("Erro: AGENTMAIL_API_KEY não encontrada no arquivo .env.")
        return
        
    print(f"Conectando ao AgentMail e monitorando a inbox: {inbox_id}...")
    
    try:
        am = AgentMail(api_key=api_key)
        
        # List received messages in the inbox
        res = am.inboxes.messages.list(inbox_id=inbox_id)
        messages = res.messages if res and hasattr(res, "messages") else []
        
        if not messages:
            print("Nenhuma mensagem encontrada na caixa de entrada.")
            return
            
        print(f"Total de mensagens encontradas: {len(messages)}. Buscando por anexo MP4...")
        
        target_attachment = None
        target_msg_id = None
        
        # Iterate over messages, starting from the most recent
        for msg in messages:
            msg_attachments = getattr(msg, "attachments", []) or []
            for att in msg_attachments:
                filename = getattr(att, "filename", "") or ""
                if filename.lower().endswith(".mp4"):
                    print(f"Encontrado anexo qualificado: '{filename}' (ID: {att.attachment_id}) na mensagem '{msg.subject}'")
                    target_attachment = att
                    target_msg_id = msg.message_id
                    break
            if target_attachment:
                break
                
        if not target_attachment:
            print("Nenhum anexo .mp4 encontrado nas mensagens recebidas.")
            return
            
        print(f"Solicitando URL de download para o anexo '{target_attachment.filename}'...")
        att_res = am.inboxes.messages.get_attachment(
            inbox_id=inbox_id,
            message_id=target_msg_id,
            attachment_id=target_attachment.attachment_id
        )
        
        download_url = getattr(att_res, "download_url", None)
        if not download_url:
            print("Erro: Não foi possível obter o link de download do anexo.")
            return
            
        # Ensure uploads directory exists
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
        os.makedirs(uploads_dir, exist_ok=True)
        
        dest_path = os.path.join(uploads_dir, "samplevideo.mp4")
        print(f"Baixando vídeo e salvando localmente em: {dest_path}...")
        
        # Stream download the file
        res_file = requests.get(download_url, stream=True)
        res_file.raise_for_status()
        
        with open(dest_path, "wb") as f:
            for chunk in res_file.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        print("Download concluído com absoluto sucesso!")
        print(f"O vídeo exemplo local está pronto para uso em {dest_path}")
        
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}")

if __name__ == "__main__":
    main()