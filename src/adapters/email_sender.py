import smtplib
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
import logging


logger = logging.getLogger(__name__)


class EmailSender(ABC):
    @abstractmethod
    async def send_email_html(self, to: str, subject: str, body: str):
        raise NotImplementedError


class SMTPEmailSender(EmailSender):
    def __init__(self,
                 smtp_server: str,
                 smtp_port: int,
                 smtp_username: str,
                 smtp_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    async def send_email_html(self, to: str, subject: str, body: str):
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = self.smtp_username
        msg['To'] = to

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.login(self.smtp_username, self.smtp_password)
                server.auth_plain()
                server.send_message(msg)
                logger.info(f"Email sent to {to} with subject '{subject}'")
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            raise e