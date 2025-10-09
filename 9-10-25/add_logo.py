#!/usr/bin/env python3
"""
Logo ekleme scripti - Ablaların Yeri restoranı için
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_logo():
    """Placeholder logo oluştur"""
    
    # Logo boyutları
    size = (200, 200)
    
    # Yeni resim oluştur
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Arka plan dairesi (sarı)
    draw.ellipse([10, 10, 190, 190], fill=(255, 215, 0, 255), outline=(255, 165, 0, 255), width=3)
    
    # Nazar boncuğu (üstte)
    draw.ellipse([85, 20, 115, 50], fill=(0, 0, 139, 255), outline=(0, 0, 255, 255), width=2)
    draw.ellipse([90, 25, 110, 45], fill=(0, 0, 255, 255), outline=(173, 216, 230, 255), width=1)
    draw.ellipse([95, 30, 105, 40], fill=(255, 255, 255, 255))
    draw.ellipse([98, 33, 102, 37], fill=(0, 0, 0, 255))
    
    # Yemek tabağı
    draw.ellipse([50, 80, 150, 120], fill=(255, 255, 255, 255), outline=(200, 200, 200, 255), width=2)
    
    # Yemek (kebap)
    draw.rectangle([70, 90, 130, 110], fill=(139, 69, 19, 255))
    
    # Sos
    draw.ellipse([60, 100, 80, 110], fill=(255, 0, 0, 255))
    draw.ellipse([120, 100, 140, 110], fill=(255, 0, 0, 255))
    
    # Kareli masa örtüsü
    for i in range(0, 200, 20):
        for j in range(0, 200, 20):
            if (i // 20 + j // 20) % 2 == 0:
                draw.rectangle([i, j, i+20, j+20], fill=(255, 0, 0, 50))
    
    # Metin ekleme (basit)
    try:
        # Font boyutu
        font_size = 16
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Varsayılan font
        font = ImageFont.load_default()
    
    # "ABLALARIN YERI" yazısı
    text = "ABLALARIN\nYERI"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2 - 20
    
    draw.text((x, y), text, fill=(139, 69, 19, 255), font=font, align='center')
    
    # Klasör oluştur
    os.makedirs('static/images', exist_ok=True)
    
    # Logo kaydet
    img.save('static/images/logo.png', 'PNG')
    print("✅ Placeholder logo oluşturuldu: static/images/logo.png")
    print("📝 Gerçek logonuzu bu dosyayla değiştirebilirsiniz.")

if __name__ == '__main__':
    create_placeholder_logo()
