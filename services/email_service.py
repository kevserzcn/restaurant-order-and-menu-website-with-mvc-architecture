"""
E-posta Gönderim Servisi
========================
SMTP protokolü ile e-posta gönderimi sağlayan servis.

Fonksiyonlar:
- send_invoice_email(recipient, pdf_path): Fatura PDF'ini e-posta ile gönder

Özellikler:
- SMTP sunucusu desteği (Gmail varsayılan)
- TLS şifreleme
- PDF ek dosya gönderimi
- HTML e-posta içeriği
- Hata yönetimi

Yapılandırma (.env):
- MAIL_SERVER: SMTP sunucu adresi (smtp.gmail.com)
- MAIL_PORT: SMTP portu (587)
- MAIL_USERNAME: Gönderici e-posta
- MAIL_PASSWORD: E-posta şifresi/app password
- MAIL_USE_TLS: TLS kullanımı (true)

Güvenlik:
- Gmail için "App Password" kullanın
- 2FA aktif olmalı

Kullanım:
    success = send_invoice_email('customer@example.com', 'invoice.pdf')
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app


def send_otp_email(recipient_email: str, otp_code: str) -> bool:
    """Send OTP code to the given email address using SMTP settings.
    
    Returns True on success, False otherwise. Falls back to console print if misconfigured.
    """
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = int(current_app.config.get('MAIL_PORT') or 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')

    # If email not configured, simulate send (for testing)
    if not mail_server or not mail_username or not mail_password:
        print(f"⚠️  EMAIL NOT CONFIGURED - SIMULATED EMAIL:")
        print(f"   To: {recipient_email}")
        print(f"   OTP Code: {otp_code}")
        print(f"   ⚠️  In production, configure MAIL_SERVER, MAIL_USERNAME, and MAIL_PASSWORD in .env file")
        return True

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
    """Send contact form submission to admin email.
    
    Returns True on success, False otherwise. Falls back to console print if misconfigured.
    """
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = int(current_app.config.get('MAIL_PORT') or 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')

    # Admin e-posta adresi
    admin_email = 'ablalar42@gmail.com'

    # If email not configured, simulate send (for testing)
    if not mail_server or not mail_username or not mail_password:
        print(f"⚠️  EMAIL NOT CONFIGURED - SIMULATED CONTACT EMAIL:")
        print(f"   To: {admin_email}")
        print(f"   From: {contact_name} ({contact_email})")
        print(f"   Type: {contact_type}")
        print(f"   Rating: {rating} stars" if rating else "   Rating: None")
        print(f"   Message: {message}")
        return True

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


def send_reply_email(recipient_email: str, contact_name: str, contact_type: str, original_message: str, admin_reply: str, admin_name: str = None) -> bool:
    """Send admin reply to customer email.
    
    Returns True on success, False otherwise. Falls back to console print if misconfigured.
    """
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = int(current_app.config.get('MAIL_PORT') or 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')

    # If email not configured, simulate send (for testing)
    if not mail_server or not mail_username or not mail_password:
        print(f"⚠️  EMAIL NOT CONFIGURED - SIMULATED REPLY EMAIL:")
        print(f"   To: {recipient_email}")
        print(f"   Subject: Ablaların Yeri - Mesajınıza Cevap")
        print(f"   Original Message: {original_message}")
        print(f"   Admin Reply: {admin_reply}")
        print(f"   ⚠️  In production, configure MAIL_SERVER, MAIL_USERNAME, and MAIL_PASSWORD in .env file")
        return True

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

