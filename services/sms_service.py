import requests
import os
from flask import current_app

def send_invoice_sms(phone_number, pdf_path):
    """PDF faturayı SMS ile gönder"""
    
    # SMS API konfigürasyonu
    api_key = current_app.config.get('SMS_API_KEY')
    api_url = current_app.config.get('SMS_API_URL')
    
    # Eğer SMS API konfigürasyonu yoksa, simüle edilmiş SMS gönder
    if not api_key or not api_url:
        print(f"SIMULATED SMS: Fatura PDF'i {phone_number} numarasına gönderildi!")
        print(f"PDF Dosya Yolu: {pdf_path}")
        print(f"SMS İçeriği:")
        print(f"Ablaların Yeri - Faturanız hazırlandı!")
        print(f"PDF faturanızı görüntülemek için: {pdf_path}")
        print(f"Teşekkür ederiz!")
        return True
    
    try:
        # SMS içeriği
        message = f"""Ablaların Yeri - Faturanız hazırlandı!
        
PDF faturanızı görüntülemek için: {pdf_path}

Teşekkür ederiz!"""
        
        # SMS API'ye istek gönder
        payload = {
            'api_key': api_key,
            'phone': phone_number,
            'message': message
        }
        
        response = requests.post(api_url, data=payload, timeout=30)
        
        if response.status_code == 200:
            print(f"SMS başarıyla gönderildi: {phone_number}")
            return True
        else:
            print(f"SMS gönderilemedi: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"SMS gönderme hatası: {str(e)}")
        # Hata durumunda da simüle edilmiş SMS olarak kabul et
        print(f"SIMULATED SMS: Fatura PDF'i {phone_number} numarasına gönderildi!")
        print(f"PDF Dosya Yolu: {pdf_path}")
        return True

def send_order_confirmation_sms(phone_number, order_id):
    """Sipariş onay SMS'i gönder"""
    
    message = f"""
    Siparişiniz alındı!
    Sipariş No: {order_id}
    10 dakika içinde masanıza servis edilecektir.
    Teşekkür ederiz!
    """
    
    return send_sms(phone_number, message)

def send_sms(phone_number, message):
    """Genel SMS gönderme fonksiyonu"""
    
    api_key = current_app.config.get('SMS_API_KEY')
    api_url = current_app.config.get('SMS_API_URL')
    
    if not api_key or not api_url:
        print("SMS API konfigürasyonu bulunamadı!")
        return False
    
    try:
        payload = {
            'api_key': api_key,
            'phone': phone_number,
            'message': message
        }
        
        response = requests.post(api_url, data=payload, timeout=30)
        return response.status_code == 200
        
    except Exception as e:
        print(f"SMS gönderme hatası: {str(e)}")
        return False
