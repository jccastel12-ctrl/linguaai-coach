"""Minimal email adapter. No third-party dependency is required for the MVP."""

import logging
import smtplib
from email.message import EmailMessage

from anyio import to_thread

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(*, to: str, subject: str, text: str) -> bool:
    """Send through configured transport. Returns False when delivery is disabled/fails."""
    if settings.email_delivery_mode == "disabled":
        logger.info("Email delivery disabled; skipped message to %s", to)
        return False
    if settings.email_delivery_mode == "console":
        logger.info("DEV EMAIL to=%s subject=%s\n%s", to, subject, text)
        return True

    if not settings.smtp_host or not settings.email_from:
        logger.error("SMTP selected but SMTP_HOST/EMAIL_FROM are missing")
        return False

    message = EmailMessage()
    message["From"] = settings.email_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(text)

    def _deliver() -> None:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as client:
            if settings.smtp_starttls:
                client.starttls()
            if settings.smtp_username:
                client.login(settings.smtp_username, settings.smtp_password.get_secret_value() if settings.smtp_password else "")
            client.send_message(message)

    try:
        await to_thread.run_sync(_deliver)
        return True
    except Exception:
        logger.exception("SMTP delivery failed for %s", to)
        return False


async def send_verification_email(email: str, raw_token: str) -> bool:
    url = f"{settings.app_public_url.rstrip('/')}/verify-email?token={raw_token}"
    return await send_email(
        to=email,
        subject="Verifica tu correo en LinguaAI Coach",
        text=f"Confirma tu correo abriendo este enlace (vence en 24 horas):\n\n{url}\n",
    )


async def send_password_reset_email(email: str, raw_token: str) -> bool:
    url = f"{settings.app_public_url.rstrip('/')}/reset-password?token={raw_token}"
    return await send_email(
        to=email,
        subject="Restablece tu contraseña de LinguaAI Coach",
        text=f"Solicitaste cambiar tu contraseña. Usa este enlace dentro de 60 minutos:\n\n{url}\n\nSi no fuiste tú, ignora este mensaje.",
    )
