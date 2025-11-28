# Restoran Menü Sistemi

Flask MVC mimarisi ile geliştirilmiş modern restoran menü ve sipariş yönetim sistemi.

## Özellikler

### Müşteri Özellikleri
- **Telefon/İsim ile Giriş**: Kullanıcılar telefon numarası ve isimleriyle giriş yapabilir
- **Menü Görüntüleme**: Kategorilere göre (yemek, tatlı, içecek, salata) ürünleri görüntüleme
- **Sepet Yönetimi**: Ürünleri sepete ekleme, miktar güncelleme, çıkarma
- **Sipariş Verme**: Sipariş oluşturma ve 10 dakika servis bildirimi
- **Ödeme Sistemi**: Nakit, kredi kartı, mobil ödeme seçenekleri
- **PDF Fatura**: Otomatik fatura oluşturma ve e-posta ile gönderim

### Admin Özellikleri
- **Email/Şifre ile Giriş**: Standart admin girişi
- **Ürün Yönetimi**: CRUD işlemleri ile ürün ekleme, düzenleme, silme
- **Masa Yönetimi**: Masa oluşturma, kapasite belirleme, garson atama
- **Garson Girişi**: Müşteri siparişlerini garsonla verme özelliği
- **Hesap Görüntüleme**: Her masanın güncel hesabını görüntüleme
- **Sipariş Takibi**: Tüm siparişleri görüntüleme ve durum güncelleme

### Teknik Özellikler
- **MVC Mimarisi**: Flask ile temiz kod yapısı
- **Responsive Tasarım**: Bootstrap ile mobil uyumlu arayüz
- **Veritabanı**: SQLite ile ilişkisel veri yönetimi
- **Authentication**: Flask-Login ile güvenli giriş sistemi
- **Form Validation**: WTForms ile form doğrulama
- **PDF Oluşturma**: ReportLab ile fatura oluşturma
- **E-posta Entegrasyonu**: SMTP ile e-posta gönderimi
- **Docker Desteği**: Konteyner tabanlı deployment

## Kurulum

### Gereksinimler
- Python 3.9+
- Docker (opsiyonel)
- Git

### Yerel Kurulum

1. **Projeyi klonlayın:**
```bash
git clone <repository-url>
cd restaurant-menu-system
```

2. **Sanal ortam oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Ortam değişkenlerini kontrol edin:**
```bash
# .env dosyası projede mevcut ve temel ayarları içerir
# Kendi e-posta ayarlarınızı kullanmak isterseniz düzenleyin
```

5. **Uygulamayı çalıştırın:**
```bash
python app.py
```

### Docker ile Kurulum

### Raporlarda Türkçe karakter (PDF/Excel)

- PDF raporları için ReportLab kullanılıyor. ReportLab varsayılan fontları Türkçe karakterleri tam desteklemeyebilir. Proje `services/pdf_service.py` içinde DejaVuSans.ttf kullanılacak şekilde yapılandırılmıştır.
- Lütfen `static/fonts/DejaVuSans.ttf` dosyasını projeye ekleyin. Eğer eklemezseniz kod otomatik olarak `Helvetica` gibi bir varsayılan font kullanır ve bazı Türkçe karakterler doğru görünmeyebilir.s

Nasıl eklenir:

1. `static/fonts` klasörünü oluşturun (varsa atlayın).
2. DejaVuSans.ttf dosyasını bu klasöre kopyalayın.

Alternatif: Üretim ortamında PDF oluşturma için sistemde yüklü bir TrueType fontun yolunu `services/pdf_service.py` içindeki `register_turkish_font()` fonksiyonuna vererek kullanabilirsiniz.


1. **Repository'yi klonlayın:**
```bash
git clone <repository-url>
cd 14-10-25
```

2. **Docker Compose ile çalıştırın:**
```bash
docker-compose up -d
```

3. **Veritabanını initialize edin (ilk kurulumda):**
```bash
docker-compose run --rm db-init
```

4. **Uygulamaya erişin:**
- Web: http://localhost:5000
- Admin: http://localhost:5000/auth/admin/login

### 📦 Veritabanı Yönetimi

**Mevcut Durum:**
- Veritabanı `instance/restaurant.db` dosyasında tutuluyor
- ✅ **Git'e dahil edildi** - Repository ile birlikte paylaşılıyor
- ✅ **Docker Volume** - Container içinde `/app/instance` klasöründe mount ediliyor
- ✅ **Kalıcı veri** - Container silinse bile veriler korunuyor

**Başka PC'de Kullanım:**
```bash
# 1. Repository'yi klonla
git clone <repository-url>

# 2. Veritabanı dosyası otomatik gelecek
# instance/restaurant.db dosyası zaten var

# 3. Docker ile çalıştır
docker-compose up -d
```

**Not:** Eğer sıfırdan başlamak isterseniz:
```bash
# Veritabanını sil ve yeniden oluştur
rm instance/restaurant.db
docker-compose run --rm db-init
```

## Kullanım

### İlk Kurulum

1. **Admin hesabı oluşturun:**
   - Email: admin@restaurant.com
   - Şifre: admin123

2. **Ürünler ekleyin:**
   - Admin paneline giriş yapın
   - Ürün Yönetimi > Yeni Ürün Ekle

3. **Masalar oluşturun:**
   - Masa Yönetimi > Yeni Masa Ekle

### Müşteri Kullanımı

1. **Kayıt olun:**
   - Ana sayfa > Müşteri Kayıt
   - Telefon numarası ve isim girin

2. **Giriş yapın:**
   - Telefon numarası ve isminizle giriş

3. **Sipariş verin:**
   - Menüyü inceleyin
   - Ürünleri sepete ekleyin
   - Sipariş verin

### Admin Kullanımı

1. **Admin paneline giriş:**
   - Email: admin@restaurant.com
   - Şifre: admin123

2. **Sistem yönetimi:**
   - Ürün ekleme/düzenleme
   - Masa yönetimi
   - Sipariş takibi
   - Hesap görüntüleme

## Proje Yapısı

```
restaurant-menu-system/
├── app.py                 # Ana uygulama dosyası
├── config.py             # Konfigürasyon
├── requirements.txt      # Python bağımlılıkları
├── models/               # Veritabanı modelleri
│   ├── user.py
│   ├── admin.py
│   ├── product.py
│   ├── order.py
│   ├── table.py
│   └── payment.py
├── controllers/          # MVC Controllers
│   ├── auth_controller.py
│   ├── admin_controller.py
│   ├── user_controller.py
│   └── api_controller.py
├── services/            # İş mantığı servisleri
│   ├── pdf_service.py
│   └── email_service.py
├── views/               # HTML şablonları (View katmanı)
│   ├── base.html
│   ├── auth/
│   ├── user/
│   └── admin/
├── static/             # Statik dosyalar
│   ├── css/
│   ├── js/
│   └── invoices/
├── forms.py            # WTForms formları
├── extensions.py       # Flask uzantıları
└── Dockerfile         # Docker konfigürasyonu
```

## API Endpoints

### Authentication
- `GET /auth/login` - Giriş sayfası
- `POST /auth/user/login` - Müşteri girişi
- `POST /auth/admin/login` - Admin girişi
- `GET /auth/logout` - Çıkış

### User
- `GET /user/dashboard` - Müşteri ana sayfa
- `GET /user/menu` - Menü görüntüleme
- `POST /user/add-to-cart` - Sepete ekleme
- `GET /user/cart` - Sepet görüntüleme
- `POST /user/place-order` - Sipariş verme
- `GET /user/checkout` - Ödeme sayfası
- `POST /user/payment` - Ödeme işlemi

### Admin
- `GET /admin/dashboard` - Admin ana sayfa
- `GET /admin/products` - Ürün listesi
- `POST /admin/add-product` - Ürün ekleme
- `GET /admin/tables` - Masa listesi
- `GET /admin/table/<id>` - Masa detayları
- `POST /admin/table/<id>/add-item` - Masaya ürün ekleme

### API
- `GET /api/products` - Ürün listesi (JSON)
- `GET /api/products/<category>` - Kategoriye göre ürünler
- `GET /api/tables` - Masa listesi (JSON)
- `GET /api/search?q=<query>` - Ürün arama

## Veritabanı Şeması

### Users (Müşteriler)
- id, phone, name, created_at, is_active

### Admins (Yöneticiler)
- id, email, password_hash, name, created_at, is_active

### Products (Ürünler)
- id, name, description, price, category, image_url, is_available

### Tables (Masalar)
- id, table_number, capacity, is_occupied, waiter_name

### Orders (Siparişler)
- id, user_id, table_id, total_amount, status, created_at

### OrderItems (Sipariş Kalemleri)
- id, order_id, product_id, quantity, price

### Payments (Ödemeler)
- id, order_id, amount, payment_method, status, transaction_id

## Güvenlik

- **Authentication**: Flask-Login ile güvenli giriş
- **Authorization**: Rol tabanlı yetkilendirme
- **CSRF Protection**: WTForms ile CSRF koruması
- **Input Validation**: Form doğrulama
- **SQL Injection**: SQLAlchemy ORM koruması

## Deployment

### Production Ayarları

1. **Ortam değişkenleri:**
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:pass@host:port/db
```

2. **Güvenlik:**
- HTTPS kullanın
- Güçlü şifreler
- Düzenli güncellemeler

3. **Performans:**
- Redis cache
- Nginx reverse proxy
- Database optimization

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

- Proje Sahibi: Kevser ÖZCAN
- Email: kevser_ozcan03@hotmail.com
- GitHub: kevserzcn

## Changelog

### v1.0.0
- İlk sürüm
- Temel MVC mimarisi
- Müşteri ve admin panelleri
- Sipariş yönetimi
- PDF fatura oluşturma
- E-posta entegrasyonu
- Docker desteği
#

