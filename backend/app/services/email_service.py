from abc import ABC, abstractmethod
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader
from email.message import EmailMessage

from app.core.config import Settings, get_settings

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"
_jinja_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=True)


class EmailSender(ABC):
    @abstractmethod
    async def send_verification_email(self, to: str, token: str) -> None: ...


class SMTPEmailSender(EmailSender):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send_verification_email(self, to: str, token: str) -> None:
        verify_url = f"{self._settings.frontend_url}/verify-email?token={token}"
        template = _jinja_env.get_template("verify_email.html")
        html_body = template.render(verify_url=verify_url)

        message = EmailMessage()
        message["From"] = self._settings.smtp_from_email
        message["To"] = to
        message["Subject"] = "Verify your email address"
        message.set_content(f"Please verify your email by visiting: {verify_url}")
        message.add_alternative(html_body, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=self._settings.smtp_host,
            port=self._settings.smtp_port,
            username=self._settings.smtp_username,
            password=self._settings.smtp_password,
            start_tls=self._settings.smtp_use_tls,
        )


def get_email_sender() -> EmailSender:
    return SMTPEmailSender(get_settings())
