from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from utils.datetime_utils import format_local
import os

def generate_invoice_pdf(order):
    """Sipariş için PDF fatura oluştur"""
    
    # PDF dosya yolu
    timestamp = format_local(datetime.utcnow(), '%Y%m%d_%H%M%S')
    filename = f"invoice_{order.id}_{timestamp}.pdf"
    filepath = os.path.join('static', 'invoices', filename)
    
    # Dizin yoksa oluştur
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # PDF oluştur
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    # Stil tanımlamaları
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Başlık
    title = Paragraph("RESTORAN FATURASI", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Müşteri bilgileri
    from models import User
    user = User.query.get(order.user_id)
    customer_info = f"""
    <b>Müşteri:</b> {user.name if user else 'Bilinmiyor'}<br/>
    <b>E-posta:</b> {user.email if user else 'Bilinmiyor'}<br/>
    <b>Sipariş Tarihi:</b> {format_local(order.created_at)}<br/>
    <b>Sipariş No:</b> {order.id}
    """
    story.append(Paragraph(customer_info, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Sipariş detayları tablosu
    table_data = [['Ürün', 'Miktar', 'Birim Fiyat', 'Toplam']]
    
    for item in order.items:
        table_data.append([
            item.product.name,
            str(item.quantity),
            f"{item.price:.2f} ₺",
            f"{item.quantity * item.price:.2f} ₺"
        ])
    
    # Toplam satırı
    table_data.append(['', '', 'TOPLAM:', f"{order.total_amount:.2f} ₺"])
    
    # Tablo oluştur
    table = Table(table_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Teşekkür mesajı
    thanks = Paragraph("Teşekkür ederiz!<br/>Yeniden bekleriz.", styles['Normal'])
    story.append(thanks)
    
    # PDF'i oluştur
    doc.build(story)
    return filepath
    
def generate_report_pdf(payments):
    """Rapor için PDF oluştur"""
    
    # PDF dosya yolu
    timestamp = format_local(datetime.utcnow(), '%Y%m%d_%H%M%S')
    filename = f"rapor_{timestamp}.pdf"
    filepath = os.path.join('static', 'reports', filename)
    
    # Dizin yoksa oluştur
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # PDF oluştur
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    # Stil tanımlamaları
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Başlık
    title = Paragraph("ABLALARIN YERİ - GELİR RAPORU", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Rapor tarihi
    report_date = f"Rapor Tarihi: {format_local(datetime.utcnow())}"
    story.append(Paragraph(report_date, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Toplam gelir
    total_amount = sum(p.amount for p in payments)
    total_info = f"<b>Toplam Gelir:</b> {total_amount:.2f} ₺"
    story.append(Paragraph(total_info, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Ödemeler tablosu
    table_data = [['Ödeme ID', 'Sipariş ID', 'Masa', 'Müşteri', 'Tutar', 'Yöntem', 'Tarih']]
    
    for payment in payments:
        # Order ve User bilgilerini güvenli şekilde al
        order = payment.order
        table_number = 'N/A'
        user_name = 'N/A'
        
        if order:
            if hasattr(order, 'table') and order.table:
                table_number = str(order.table.table_number)
            if hasattr(order, 'user') and order.user:
                user_name = order.user.name
        
        table_data.append([
            str(payment.id),
            str(payment.order_id),
            table_number,
            user_name,
            f"{payment.amount:.2f} ₺",
            payment.payment_method.title(),
            format_local(payment.created_at)
        ])
    
    # Tablo oluştur
    table = Table(table_data, colWidths=[1*inch, 1*inch, 0.8*inch, 1.5*inch, 1*inch, 1*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Teşekkür mesajı
    thanks = Paragraph("Rapor tamamlandı.<br/>Ablaların Yeri", styles['Normal'])
    story.append(thanks)
    
    # PDF'i oluştur
    doc.build(story)
    
    return filepath
