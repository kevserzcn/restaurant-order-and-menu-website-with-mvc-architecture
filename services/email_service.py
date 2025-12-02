import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app


def send_otp_email(recipient_email: str, otp_code: str) -> bool:
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = int(current_app.config.get('MAIL_PORT') or 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')

    if not mail_server or not mail_username or not mail_password:
        raise ValueError("Email configuration is missing. Please configure MAIL_SERVER, MAIL_USERNAME, and MAIL_PASSWORD.")

    msg = MIMEMultipart()
    msg['From'] = mail_username
    msg['To'] = recipient_email
    msg['Subject'] = 'Ablaların Yeri - Şifre Sıfırlama Kodu'

    body = f"""
Merhaba,

Şifre sıfırlama kodunuz:

{otp_code}

Bu kod 10 dakika geçerlidir.

Eğer bu işlemi siz yapmadıysanız, lütfen bu e-postayı görmezden gelin.

Teşekkürler,
Ablaların Yeri
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

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
        return False


def send_contact_email(contact_name: str, contact_email: str, contact_type: str, message: str, rating: int = None) -> bool:
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = int(current_app.config.get('MAIL_PORT') or 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')

    admin_email = current_app.config.get('ADMIN_EMAIL', 'ablalar42@gmail.com')

    if not mail_server or not mail_username or not mail_password:
        raise ValueError("Email configuration is missing. Please configure MAIL_SERVER, MAIL_USERNAME, and MAIL_PASSWORD.")

    msg = MIMEMultipart()
    msg['From'] = mail_username
    msg['To'] = admin_email
    msg['Subject'] = f'Ablaların Yeri - {contact_type.title()} - {contact_name}'

    type_display = {
        'request': 'İstek',
        'complaint': 'Şikayet',
        'comment': 'Yorum'
    }.get(contact_type, contact_type)

    body = f"""
Yeni İletişim Formu Mesajı

İletişim Tipi: {type_display}
Gönderen: {contact_name}
E-posta: {contact_email}
"""
    if rating:
        body += f"Puan: {'⭐' * rating} ({rating}/5)\n"
    
    body += f"""
Mesaj:
{message}

---
Bu mesaj müşteri iletişim formundan gönderilmiştir.
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(mail_server, mail_port, timeout=30)
        if mail_use_tls:
            server.starttls()
        server.login(mail_username, mail_password)
        server.sendmail(mail_username, admin_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"EMAIL SEND ERROR: {e}")
        return False


def send_invoice_email(recipient_email: str, pdf_path: str) -> bool:

    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = int(current_app.config.get('MAIL_PORT') or 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')

    if not mail_server or not mail_username or not mail_password:
        raise ValueError("Email configuration is missing. Please configure MAIL_SERVER, MAIL_USERNAME, and MAIL_PASSWORD.")

    msg = MIMEMultipart()
    msg['From'] = mail_username
    msg['To'] = recipient_email
    msg['Subject'] = 'Ablaların Yeri - Faturanız'

    body = 'Faturanızı ekte PDF olarak bulabilirsiniz. Teşekkür ederiz.'
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

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
        return False


def send_reply_email(recipient_email: str, contact_name: str, contact_type: str, original_message: str, admin_reply: str, admin_name: str = None) -> bool:
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = int(current_app.config.get('MAIL_PORT') or 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')

    if not mail_server or not mail_username or not mail_password:
        raise ValueError("Email configuration is missing. Please configure MAIL_SERVER, MAIL_USERNAME, and MAIL_PASSWORD.")

    msg = MIMEMultipart()
    msg['From'] = mail_username
    msg['To'] = recipient_email
    msg['Subject'] = 'Ablaların Yeri - Mesajınıza Cevap'

    type_display = {
        'request': 'İstek',
        'complaint': 'Şikayet',
        'comment': 'Yorum'
    }.get(contact_type, contact_type)

    body = f"""
Merhaba {contact_name},

{type_display} mesajınıza cevap vermek istiyoruz.

Sizin Mesajınız:
{original_message}

---
Cevabımız:
{admin_reply}
---
"""
    if admin_name:
        body += f"\nSaygılarımızla,\n{admin_name}\nAblaların Yeri"
    else:
        body += "\nSaygılarımızla,\nAblaların Yeri Ekibi"

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

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
        return False

