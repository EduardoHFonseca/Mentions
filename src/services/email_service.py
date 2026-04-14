import os
import requests
from typing import Optional, List, Union
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

class EmailService:
    """
    Serviço centralizado para envio de e-mails via AgentMail.
    Ideal para notificações de ocorrências e envio de relatórios.
    """

    def __init__(self, api_key: Optional[str] = None, inbox_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("AGENTMAIL_API_KEY")
        self.inbox_id = inbox_id or os.getenv("AGENTMAIL_INBOX_ID", "argo9000@agentmail.to")
        self.base_url = "https://api.agentmail.to/v0"
        
        if not self.api_key:
            raise ValueError("AGENTMAIL_API_KEY não encontrada no ambiente.")

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_notification(
        self, 
        to: Union[str, List[str]], 
        subject: str, 
        text: str, 
        html: Optional[str] = None,
        inbox_id: Optional[str] = None
    ) -> dict:
        """
        Envia uma notificação rápida de ocorrência encontrada.
        """
        target_inbox = inbox_id or self.inbox_id
        url = f"{self.base_url}/inboxes/{target_inbox}/messages/send"
        
        payload = {
            "to": to,
            "subject": subject,
            "text": text,
        }
        if html:
            payload["html"] = html
            
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def send_report(
        self, 
        to: Union[str, List[str]], 
        subject: str, 
        text: str, 
        filename: str, 
        content: str, 
        content_type: str = "application/pdf"
    ) -> dict:
        """
        Envia um relatório com anexo (CSV ou PDF).
        """
        target_inbox = self.inbox_id
        url = f"{self.base_url}/inboxes/{target_inbox}/messages/send"
        
        attachments = [{
            "filename": filename,
            "content_type": content_type,
            "content": content,
            "content_disposition": "attachment"
        }]
        
        payload = {
            "to": to,
            "subject": subject,
            "text": text,
            "attachments": attachments
        }
        
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

# Instância Singleton para uso em todo o sistema
email_service = EmailService()
