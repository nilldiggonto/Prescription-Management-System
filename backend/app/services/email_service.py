from abc import ABC, abstractmethod
from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core.config import Settings, get_settings

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"
_jinja_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=True)


class EmailSender(ABC):
    @abstractmethod
    async def send_verification_otp(self, to: str, otp: str, expire_minutes: int) -> None: ...

    @abstractmethod
    async def send_password_reset_otp(self, to: str, otp: str, expire_minutes: int) -> None: ...


class SMTPEmailSender(EmailSender):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send_verification_otp(self, to: str, otp: str, expire_minutes: int) -> None:
        await self._send_otp_email(
            to=to,
            subject="Your verification code",
            template_name="verify_otp.html",
            otp=otp,
            expire_minutes=expire_minutes,
        )

    async def send_password_reset_otp(self, to: str, otp: str, expire_minutes: int) -> None:
        await self._send_otp_email(
            to=to,
            subject="Your password reset code",
            template_name="reset_password_otp.html",
            otp=otp,
            expire_minutes=expire_minutes,
        )

    async def _send_otp_email(self, *, to: str, subject: str, template_name: str, otp: str, expire_minutes: int) -> None:
        template = _jinja_env.get_template(template_name)
        html_body = template.render(otp=otp, expire_minutes=expire_minutes)

        message = EmailMessage()
        message["From"] = self._settings.smtp_from_email
        message["To"] = to
        message["Subject"] = subject
        message.set_content(f"Your code is: {otp}\nThis code expires in {expire_minutes} minutes.")
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