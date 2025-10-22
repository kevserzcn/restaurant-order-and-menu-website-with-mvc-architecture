"""
SMS Servisi - Fatura göndermek için SMS işlemleri
"""
from flask import current_app
import requests


def send_invoice_sms(phone_number, order_id, amount, pdf_url=None):
    """
    Müşteriye fatura SMS'i gönder
    
    Args:
        phone_number: Müşteri telefon numarası
        order_id: Sipariş ID
        amount: Ödeme tutarı
        pdf_url: PDF fatura linki (opsiyonel)
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        # SMS API ayarları
        api_key = current_app.config.get('SMS_API_KEY')
        api_url = current_app.config.get('SMS_API_URL')
        
        # API key yoksa sadece log at
        if not api_key or not api_url:
            current_app.logger.info(f"SMS gönderimi simüle edildi: {phone_number} - Sipariş #{order_id} - {amount} TL")
            return True
        
        # SMS içeriği
        message = f"Ablaların Yeri - Sipariş #{order_id} için {amount} TL ödemeniz alınmıştır. Teşekkür ederiz!"
        
        if pdf_url:
            message += f" Faturanız: {pdf_url}"
        
        # SMS API'ye istek gönder
        payload = {
            'api_key': api_key,
            'phone': phone_number,
            'message': message
        }
        
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            current_app.logger.info(f"SMS başarıyla gönderildi: {phone_number}")
            return True
        else:
            current_app.logger.error(f"SMS gönderimi başarısız: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"SMS gönderimi sırasında hata: {str(e)}")
        return False


def send_order_notification_sms(phone_number, table_name, order_items):
    """
    Sipariş bildirimi SMS'i gönder
    
    Args:
        phone_number: Müşteri telefon numarası
        table_name: Masa adı
        order_items: Sipariş kalemleri
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        api_key = current_app.config.get('SMS_API_KEY')
        api_url = current_app.config.get('SMS_API_URL')
        
        if not api_key or not api_url:
            current_app.logger.info(f"Sipariş bildirimi SMS'i simüle edildi: {phone_number} - {table_name}")
            return True
        
        # SMS içeriği
        message = f"Ablaların Yeri - {table_name} masasına siparişiniz alınmıştır. Afiyet olsun!"
        
        payload = {
            'api_key': api_key,
            'phone': phone_number,
            'message': message
        }
        
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            current_app.logger.info(f"Sipariş bildirimi SMS'i başarıyla gönderildi: {phone_number}")
            return True
        else:
            current_app.logger.error(f"Sipariş bildirimi SMS'i başarısız: {response.status_code}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Sipariş bildirimi SMS'i sırasında hata: {str(e)}")
        return False
