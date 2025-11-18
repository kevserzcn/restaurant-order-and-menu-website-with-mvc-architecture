import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app


def send_invoice_email(recipient_email: str, pdf_path: str) -> bool:
    """Send invoice PDF to the given email address using SMTP settings.

    Returns True on success, False otherwise. Falls back to console print if misconfigured.
    """

    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = int(current_app.config.get('MAIL_PORT') or 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')

    # If email not configured, simulate send
    if not mail_server or not mail_username or not mail_password:
        print(f"SIMULATED EMAIL: Sent invoice to {recipient_email}")
        print(f"Attachment: {pdf_path}")
        return True

    msg = MIMEMultipart()
    msg['From'] = mail_username
    msg['To'] = recipient_email
    msg['Subject'] = 'Ablaların Yeri - Faturanız'

    body = 'Faturanızı ekte PDF olarak bulabilirsiniz. Teşekkür ederiz.'
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Attach PDF
    try:
        with open(pdf_path, 'rb') as attachment_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(pdf_path)}"')
        msg.attach(part)
    except Exception as e:
        print(f"EMAIL ATTACH ERROR: {e}")
        return False

    try:
        server = smtplib.SMTP(mail_server, mail_port, timeout=30)
        if mail_use_tls:
            server.starttls()
        server.login(mail_username, mail_password)
        server.sendmail(mail_username, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"EMAIL SEND ERROR: {e}")
        # Gerçek gönderim hatasında başarısız dön
        return False


