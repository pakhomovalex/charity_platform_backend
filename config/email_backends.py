import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class SendGridBackend(BaseEmailBackend):
    """Custom email backend using SendGrid Web API."""
    
    def send_messages(self, email_messages):
        api_key = os.getenv('SENDGRID_API_KEY')
        
        if not api_key:
            logger.error("SENDGRID_API_KEY is not set")
            return 0
            
        sg = SendGridAPIClient(api_key)
        sent = 0
        
        for msg in email_messages:
            message = Mail(
                from_email=msg.from_email,
                to_emails=msg.to,
                subject=msg.subject,
                plain_text_content=msg.body,
            )
            
            try:
                response = sg.send(message)
                logger.info(f"SendGrid status: {response.status_code}")
                if response.status_code == 202:
                    sent += 1
            except Exception as e:
                logger.error(f"SendGrid error: {e}")
                
        return sent