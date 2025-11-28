"""
OTP Servisi
===========
Şifre sıfırlama için OTP kod üretme ve doğrulama.

Fonksiyonlar:
- generate_otp(): 6 haneli OTP kodu üret
- send_otp(): OTP kodunu e-posta ile gönder
- verify_otp(): OTP kodunu doğrula
- cleanup_expired_otps(): Süresi dolmuş OTP'leri temizle
"""

import random
from datetime import datetime
from models.otp import OTP
from extensions import db
from services.email_service import send_otp_email

def generate_otp_code() -> str:
    """6 haneli OTP kodu üret"""
    return str(random.randint(100000, 999999))

def create_and_send_otp(email: str) -> tuple[bool, str]:
    """OTP kodu oluştur ve gönder
    
    Returns:
        (success: bool, message: str)
    """
    # Eski OTP'leri temizle
    cleanup_expired_otps(email)
    
    # Yeni OTP kodu oluştur
    otp_code = generate_otp_code()
    
    # OTP kaydı oluştur
    otp = OTP(email=email, code=otp_code, expires_in_minutes=10)
    db.session.add(otp)
    db.session.commit()
    
    # E-posta gönder (ablalar42@gmail.com'a)
    recipient_email = 'ablalar42@gmail.com'
    success = send_otp_email(recipient_email, otp_code)
    
    if success:
        return True, "Doğrulama kodu e-posta adresinize gönderildi."
    else:
        # E-posta gönderilemedi, OTP kaydını sil
        db.session.delete(otp)
        db.session.commit()
        return False, "E-posta gönderilemedi. Lütfen tekrar deneyin."

def verify_otp(email: str, code: str) -> tuple[bool, str, OTP]:
    """OTP kodunu doğrula
    
    Returns:
        (is_valid: bool, message: str, otp: OTP or None)
    """
    # En son gönderilen geçerli OTP'yi bul
    otp = OTP.query.filter_by(
        email=email,
        used=False
    ).order_by(OTP.created_at.desc()).first()
    
    if not otp:
        return False, "Geçersiz veya süresi dolmuş kod.", None
    
    if not otp.is_valid():
        return False, "Kodun süresi dolmuş. Lütfen yeni kod talep edin.", None
    
    if otp.code != code:
        return False, "Geçersiz kod. Lütfen tekrar deneyin.", None
    
    # Kod doğru, kullanıldı olarak işaretle
    otp.mark_as_used()
    return True, "Kod doğrulandı.", otp

def cleanup_expired_otps(email: str = None):
    """Süresi dolmuş OTP'leri temizle"""
    query = OTP.query.filter(
        (OTP.expires_at < datetime.utcnow()) | (OTP.used == True)
    )
    
    if email:
        query = query.filter_by(email=email)
    
    expired_otps = query.all()
    for otp in expired_otps:
        db.session.delete(otp)
    
    db.session.commit()



