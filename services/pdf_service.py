from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from utils.datetime_utils import format_local
import os

def register_turkish_font():
    font_path = os.path.join('static', 'fonts', 'DejaVuSans.ttf')
    font_bold_path = os.path.join('static', 'fonts', 'DejaVuSans-Bold.ttf')
    
    if not os.path.exists(font_path):
        return 'Helvetica'
    
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    if os.path.exists(font_bold_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))
    
    return 'DejaVuSans'

def generate_invoice_pdf(order):
    
    timestamp = format_local(datetime.utcnow(), '%Y%m%d_%H%M%S')
    filename = f"invoice_{order.id}_{timestamp}.pdf"
    filepath = os.path.join('static', 'invoices', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    font_name = register_turkish_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        spaceAfter=30,
        alignment=1  
    )
    
    title = Paragraph("RESTORAN FATURASI", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    from models import User
    user = User.query.get(order.user_id)
    customer_info = f"""
    <b>Müşteri:</b> {user.name if user else 'Bilinmiyor'}<br/>
    <b>E-posta:</b> {user.email if user else 'Bilinmiyor'}<br/>
    <b>Sipariş Tarihi:</b> {format_local(order.created_at)}<br/>
    <b>Sipariş No:</b> {order.id}
    """
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName=font_name, encoding='utf-8')
    story.append(Paragraph(customer_info, normal_style))
    story.append(Spacer(1, 20))
    
    table_data = [['Urun', 'Miktar', 'Birim Fiyat', 'Toplam']]
    
    for item in order.items.all():
        table_data.append([
            item.product.name,
            str(item.quantity),
            f"{item.price:.2f} ₺",
            f"{item.quantity * item.price:.2f} ₺"
        ])
    
    table_data.append(['', '', 'TOPLAM:', f"{order.total_amount:.2f} ₺"])
    
    table = Table(table_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Teşekkür ederiz!<br/>Yeniden bekleriz.", normal_style))
    
    doc.build(story)
    return filepath
    
def generate_report_pdf(payments):
    
    timestamp = format_local(datetime.utcnow(), '%Y%m%d_%H%M%S')
    filename = f"rapor_{timestamp}.pdf"
    filepath = os.path.join('static', 'reports', filename)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    font_name = register_turkish_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        spaceAfter=30,
        alignment=1  
    )
    
    title = Paragraph("ABLALARIN YERİ - GELİR RAPORU", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    report_date = f"Rapor Tarihi: {format_local(datetime.utcnow())}"
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName=font_name, encoding='utf-8')
    story.append(Paragraph(report_date, normal_style))
    story.append(Spacer(1, 20))
    
    total_amount = sum(p.amount for p in payments)
    total_info = f"<b>Toplam Gelir:</b> {total_amount:.2f} ₺"
    story.append(Paragraph(total_info, normal_style))
    story.append(Spacer(1, 20))
    
    table_data = [['Ödeme ID', 'Sipariş ID', 'Masa', 'Müşteri', 'Tutar', 'Yöntem', 'Tarih']]
    
    for payment in payments:
        order = payment.order
        table_number = 'N/A'
        user_name = 'N/A'
        
        if order:
            if hasattr(order, 'table') and order.table:
                table_number = str(order.table.name)
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
    
    table = Table(table_data, colWidths=[1*inch, 1*inch, 0.8*inch, 1.5*inch, 1*inch, 1*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Rapor tamamlandı.<br/>Ablaların Yeri", normal_style))
    
    doc.build(story)
    
    return filepath
