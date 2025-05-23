# app/utils/email_utils.py
import os
import smtplib
from email.message import EmailMessage
from typing import Optional

# Lee estos valores de tus variables de entorno
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")          # tu usuario SMTP
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # tu contraseña o app-password

def send_update_email(
    to_email: str,
    report_name: str,
    report_number: int,
    feedback: Optional[str],
    updated_at: str
):
    msg = EmailMessage()
    msg["Subject"] = f"Reporte actualizado: #{report_number}"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    body = f"""
    <p>Hola,</p>
    <p>Tu reporte <strong>{report_name}</strong> (número <strong>#{report_number}</strong>) 
    fue <em>actualizado</em> el <strong>{updated_at}</strong>.</p>
    <p><strong>Retroalimentación:</strong><br/>{(feedback or 'Sin comentarios')}</p>
    """

    msg.set_content(body, subtype="html")

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)
