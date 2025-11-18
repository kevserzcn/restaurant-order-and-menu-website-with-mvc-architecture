# 📊 Veritabanı Bilgilendirmesi

## Mevcut Yapı

### Veritabanı Konumu
- **Dosya**: `instance/restaurant.db`
- **Tip**: SQLite
- **Git**: ✅ Repository'de paylaşılıyor

### Docker Yapılandırması
```yaml
volumes:
  - db_data:/app/instance   # Docker volume
```

## Kullanım Senaryoları

### 1️⃣ Geliştirme Ortamı (Development)
**Şu anki durum - önerilen:**
- ✅ Veritabanı Git'e dahil
- ✅ Tüm geliştiriciler aynı test verisine erişir
- ✅ Hızlı setup
- ⚠️ Sensitive data içeriyorsa dikkatli olun

### 2️⃣ Üretim Ortamı (Production)
**Önerilen değişiklikler:**

#### A. PostgreSQL'e Geçiş (Önerilen)
```yaml
# docker-compose.prod.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: restaurant
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

#### B. SQLite ile Devam (Küçük ölçekli projeler için)
```yaml
volumes:
  - ./instance:/app/instance  # Host'ta kalıcı
```

**.gitignore güncelle:**
```gitignore
instance/*.db
instance/*.db-journal
```

## Git ile Paylaşım

### ✅ Avantajlar
- Hızlı kurulum
- Test verisi hazır
- Tutarlı development ortamı
- Demo için uygun

### ❌ Dezavantajlar
- Hassas veriler Git'te
- Merge conflict riski
- Database size limit (>100MB GitHub uyarısı)
- Her commit'te binary file

## Öneriler

### Geliştirme İçin (Şimdiki Durum)
```bash
# .gitignore - instance/ commented out
# ✅ Veritabanı paylaşılıyor
# ✅ Seed data herkes için aynı
```

### Üretim İçin
```bash
# 1. .gitignore'a ekle
instance/*.db

# 2. Veritabanını external yapılandır
# docker-compose.prod.yml kullan

# 3. Backup stratejisi oluştur
docker exec app python -c "import shutil; shutil.copy('instance/restaurant.db', 'backup.db')"
```

## Migration Stratejisi

### SQLite → PostgreSQL
```python
# migration_script.py
from app import create_app
import os

# SQLite'tan veri çek
app = create_app()
with app.app_context():
    # Export data
    pass

# PostgreSQL'e veri yükle
os.environ['DATABASE_URL'] = 'postgresql://...'
app = create_app()
with app.app_context():
    # Import data
    pass
```

## Backup & Restore

### Backup
```bash
# Docker içinden
docker exec app cp instance/restaurant.db instance/backup_$(date +%Y%m%d).db

# Host'tan
cp instance/restaurant.db backups/restaurant_$(date +%Y%m%d).db
```

### Restore
```bash
# Docker'a restore
docker cp backup.db app:/app/instance/restaurant.db
docker-compose restart web
```

## Best Practices

1. **Development**: ✅ Veritabanını Git'e dahil et (şimdiki durum)
2. **Staging**: ⚠️ Seed script kullan, veritabanını Git'e ekleme
3. **Production**: ❌ Asla veritabanını Git'e ekleme
4. **Backup**: 📦 Düzenli backup stratejisi oluştur

## Sıkça Sorulan Sorular

### Q: Neden veritabanı sıfırlanıyor?
**A:** `.gitignore` dosyası `instance/` klasörünü ignore ediyordu. Artık düzeltildi.

### Q: Docker volume nerede tutuluyor?
**A:** Docker host'ta `/var/lib/docker/volumes/` altında (Linux/Mac) veya Docker Desktop storage'da (Windows).

### Q: Veritabanı Git'te olmalı mı?
**A:** 
- ✅ Development: Evet
- ❌ Production: Hayır

### Q: Container silersem veriler kaybolur mu?
**A:** Hayır, Docker volume kullanıldığı için veriler korunur. Ancak `docker-compose down -v` komutu volume'leri de siler.

## Sonuç

**Mevcut Durum**: ✅ Veritabanı Git'e dahil edildi
- Başka PC'de clone yapınca veritabanı gelecek
- Test verileri korunuyor
- Geliştirme için ideal

**Üretim İçin**: PostgreSQL veya external database önerilir.
