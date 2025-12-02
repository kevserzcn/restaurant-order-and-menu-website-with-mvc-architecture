import random
from datetime import datetime, timedelta
from typing import Tuple, Optional
from models.otp import OTP
from config import db
from services.email_service import send_otp_email

def generate_otp_code() -> str:
    return str(random.randint(100000, 999999))

def create_and_send_otp(email: str) -> Tuple[bool, str]:
    try:
        recent_otp = OTP.query.filter_by(email=email).filter(
            OTP.created_at > datetime.utcnow() - timedelta(minutes=1)
        ).first()
        
        if recent_otp:
            return False, "Çok sık OTP talebinde bulunuyorsunuz. 1 dakika bekleyip tekrar deneyin."
        
        cleanup_expired_otps(email)
        
        otp_code = generate_otp_code()
        
        otp = OTP(email=email, code=otp_code, expires_in_minutes=10)
        db.session.add(otp)
        db.session.commit()
        
        success = send_otp_email(email, otp_code)
        
        if success:
            return True, "Doğrulama kodu e-posta adresinize gönderildi."
        else:
            db.session.delete(otp)
            db.session.commit()
            return False, "E-posta gönderilemedi. Lütfen tekrar deneyin."
    
    except Exception as e:
        db.session.rollback()
        print(f"OTP creation error: {e}")
        return False, "Sistem hatası. Lütfen daha sonra tekrar deneyin."

def verify_otp(email: str, code: str) -> Tuple[bool, str, Optional[OTP]]:
    try:
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
        
        otp.mark_as_used()
        return True, "Kod doğrulandı.", otp
    
    except Exception as e:
        print(f"OTP verification error: {e}")
        return False, "Sistem hatası. Lütfen tekrar deneyin.", None

def cleanup_expired_otps(email: str = None):
    try:
        query = OTP.query.filter(
            (OTP.expires_at < datetime.utcnow()) | (OTP.used == True)
        )
        
        if email:
            query = query.filter_by(email=email)
        
        expired_otps = query.all()
        for otp in expired_otps:
            db.session.delete(otp)
        
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        print(f"OTP cleanup error: {e}")



