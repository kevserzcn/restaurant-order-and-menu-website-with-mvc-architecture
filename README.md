# 🍽️ Restoran Sipariş ve Menü Yönetim Sistemi

**Flask MVC** ile geliştirilmiş profesyonel, ölçeklenebilir ve modern restoran yönetim sistemi.

---

## 📖 İçindekiler

- [Genel Bakış](#-genel-bakış)
- [Özellikler](#-özellikler)
- [Mimari ve Tasarım](#-mimari-ve-tasarım)
- [Teknoloji Stack](#-teknoloji-stack)
- [Kurulum](#-kurulum)
- [Proje Yapısı](#-proje-yapısı)
- [Çalışma Mekanizması](#-çalışma-mekanizması)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Veritabanı Şeması](#-veritabanı-şeması)
- [Kullanım Senaryoları](#-kullanım-senaryoları)

---

## 🎯 Genel Bakış

Bu proje, modern restoran işletmelerinin ihtiyaçlarını karşılamak üzere tasarlanmış eksiksiz bir yönetim sistemidir. **MVC (Model-View-Controller)** mimarisi ve **SOLID** prensipleri doğrultusunda geliştirilmiş olup, bakımı kolay, genişletilebilir ve test edilebilir bir kod tabanı sunar.


---

## ✨ Özellikler

### 👥 Müşteri (User) Paneli

#### 🔐 Kimlik Doğrulama
- **Basit Kayıt**: Telefon numarası ve isim ile hızlı kayıt
- **Kolay Giriş**: Telefon numarası ile anında giriş
- **Session Yönetimi**: Güvenli oturum yönetimi

#### 📱 Menü ve Sipariş
- **Kategori Bazlı Menü**: Yemek, Tatlı, İçecek, Salata kategorileri
- **Ürün Detayları**: Fiyat, açıklama, resim görüntüleme
- **Gerçek Zamanlı Stok**: Müsait olmayan ürünler gösterilmez
- **Akıllı Sepet**:
  - Ürün ekleme/çıkarma
  - Miktar güncelleme
  - Anlık toplam hesaplama
  - Session tabanlı sepet yönetimi

#### 🏷️ Sipariş İşlemleri
- **Masa Seçimi**: Müsait masalardan seçim
- **Sipariş Özeti**: Detaylı sipariş önizleme
- **Durum Takibi**: Sipariş durumunu anlık görüntüleme
  - `Pending` → Hazırlanıyor
  - `Completed` → Hazır
  - `Payment Pending` → Ödeme bekleniyor
  - `Paid` → Ödendi

#### 💳 Ödeme Sistemi
- **Çoklu Ödeme Yöntemi**:
  - Nakit ödeme
  - Kredi kartı
- **Strategy Pattern**: Kolayca yeni ödeme yöntemleri eklenebilir
- **PDF Fatura**: Otomatik fatura oluşturma ve email gönderimi
- **Ödeme Güvenliği**: Transaction ID ile takip

#### ⭐ Değerlendirme ve İletişim
- **Sipariş Sonrası Yorum**: Puan ve yorum yazma
- **İletişim Formu**: Şikayet, öneri, talep gönderme

---

### 👨‍💼 Admin Paneli

#### 🔒 Yönetim Sistemi
- **Güvenli Giriş**: Email ve şifre ile doğrulama
- **Rol Bazlı Yetkilendirme**: Admin decorator ile korumalı endpointler
- **Dual Authentication**: User ve Admin session'ları bağımsız

#### 📦 Ürün Yönetimi
- **CRUD İşlemleri**:
  - Ürün ekleme (isim, fiyat, kategori, açıklama, resim)
  - Ürün düzenleme
  - Ürün silme
  - Ürün stok durumu güncelleme
- **Resim Yönetimi**:
  - Dosya yükleme desteği
  - URL ile resim ekleme
  - Güvenli dosya isimlendirme
- **Kategori Filtreleme**: Kategorilere göre ürün listeleme
- **Arama**: Ürün adına göre arama

#### 🪑 Masa Yönetimi
- **Masa İşlemleri**:
  - Masa oluşturma (numara, kapasite, garson)
  - Masa düzenleme
  - Masa silme
- **Doluluk Kontrolü**: Otomatik masa durumu güncelleme
- **Masa Özeti**: Her masanın güncel hesabını görüntüleme
- **Masa İstatistikleri**: Toplam, dolu, boş masa sayıları

#### 👨‍🍳 Sipariş Takibi
- **Garson Modu**: Masa başında sipariş alma
  - Masaya ürün ekleme
  - Miktar belirleme
  - Sipariş onaylama
- **Durum Güncelleme**: Sipariş durumunu değiştirme
- **Sipariş Filtreleme**:
  - Bekleyen siparişler
  - Ödeme bekleyenler
  - Tüm siparişler
- **Sipariş Detayları**: Kullanıcı, masa, ürünler, tutar bilgileri

#### 💰 Ödeme ve Hesap İşlemleri
- **Hesap Kapatma**: Masa hesabını görüntüleme ve ödeme alma
- **Ödeme Yöntemi Seçimi**: Nakit/Kart seçimi
- **Otomatik Masa Boşaltma**: Ödeme sonrası masa otomatik boşalır
- **Ödeme Geçmişi**: Tüm ödemeleri listeleme

#### 📊 Raporlama ve Analiz
- **PDF Rapor**: Gelir raporlarını PDF olarak oluşturma
- **Excel Export**: Ödeme verilerini Excel'e aktarma
- **İstatistikler**:
  - Masa doluluk oranı
  - Sipariş sayıları
  - Ödeme istatistikleri
  - Müşteri yorumları

#### 💬 Müşteri İletişimi
- **Yorum Yönetimi**: Tüm yorumları görüntüleme
- **Yorum Yanıtlama**: Müşterilere email ile cevap gönderme
- **İletişim Mesajları**: Şikayet, öneri, talepleri inceleme

---

### 🔧 Teknik Özellikler

- **🏗️ MVC Mimarisi**: Model-View-Controller ayrımı ile temiz kod
- **✨ SOLID Prensipleri**: Kurumsal seviye kod organizasyonu
- **🎨 Repository Pattern**: Veri erişim katmanı abstraction
- **🎯 Strategy Pattern**: Ödeme yöntemleri için genişletilebilir yapı
- **🎭 Service Layer**: Business logic katmanı
- **📱 Responsive Design**: Bootstrap 5 ile mobil uyumlu
- **💾 SQLAlchemy ORM**: Veritabanı yönetimi
- **🔐 Dual Authentication**: Admin ve User için ayrı session
- **✅ Form Validation**: WTForms ile güvenli form işleme
- **🛡️ CSRF Protection**: Cross-Site Request Forgery koruması
- **📧 Email Integration**: SMTP ile email gönderimi
- **📄 PDF Generation**: ReportLab ile fatura ve rapor oluşturma
- **📊 Excel Export**: OpenPyXL ile veri dışa aktarma
- **🐳 Docker Support**: Konteyner desteği
- **🌍 Türkçe Destek**: Tam Türkçe arayüz ve raporlama

---

## 🏗️ Mimari ve Tasarım

### MVC (Model-View-Controller) Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP Request/Response
┌───────────────────────────▼──────────────────────────────── ─┐
│                      FLASK APPLICATION                       │
│                          (app.py)                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐      ┌────────────────┐                  │
│  │  CONTROLLERS   │◄────►│  FORMS (WTF)   │                  │
│  │                │      │  Validation     │                 │
│  │ - auth         │      └────────────────┘                  │
│  │ - admin        │                                          │
│  │ - user         │      ┌────────────────┐                  │
│  │ - api          │◄────►│   VALIDATORS   │                  │
│  └───────┬────────┘      │  Business Rules │                 │
│          │               └────────────────┘                  │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────┐                                          │
│  │   SERVICES     │      ┌────────────────┐                  │
│  │                │◄────►│   STRATEGIES   │                  │
│  │ - Product      │      │  Payment, etc.  │                 │
│  │ - Order        │      └────────────────┘                  │
│  │ - Table        │                                          │
│  │ - Payment      │      ┌────────────────┐                  │
│  │ - Email/PDF    │◄────►│     UTILS      │                  │
│  └───────┬────────┘      │  Dual Auth, etc │                 │
│          │               └────────────────┘                  │
│          ▼                                                   │
│  ┌────────────────┐                                          │
│  │  REPOSITORIES  │                                          │
│  │                │                                          │
│  │ - Product      │                                          │
│  │ - Order        │                                          │
│  │ - Table        │                                          │
│  │ - User/Admin   │                                          │
│  │ - Payment      │                                          │
│  └───────┬────────┘                                          │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────┐                                          │
│  │    MODELS      │                                          │
│  │  (SQLAlchemy)  │                                          │
│  │                │                                          │
│  │ - User         │                                          │
│  │ - Admin        │                                          │
│  │ - Product      │                                          │
│  │ - Order        │                                          │
│  │ - Table        │                                          │
│  │ - Payment      │                                          │
│  └───────┬────────┘                                          │
│          │                                                   │
└──────────┼────────────────────────────────────────────────  ─┘
           │
           ▼
    ┌────────────┐
    │  DATABASE  │
    │  (SQLite)  │
    └────────────┘

    ┌────────────┐
    │   VIEWS    │  → Jinja2 Templates
    │  (HTML)    │
    └────────────┘
```

### Katman Sorumlulukları

#### 1️⃣ **Controllers** (İstek İşleme)
- HTTP isteklerini alır
- Form validasyonu yapar
- Service katmanını çağırır
- Response döndürür

**Örnek:**
```python
@admin_bp.route('/products/add', methods=['POST'])
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        # Validator ile kontrol
        is_valid, errors = ProductValidator.validate_product(...)
        
        # Service'i kullan
        product = product_service.create_product(...)
        
        # Response
        flash('Ürün eklendi!', 'success')
        return redirect(url_for('admin.products'))
```

#### 2️⃣ **Services** (Business Logic)
- İş kurallarını uygular
- Repository'leri kullanır
- Transaction yönetimi yapar

**Örnek:**
```python
class OrderService:
    def place_order(self, order_id, table_id):
        # İş kuralı: Sipariş boş olmamalı
        if not order.items:
            raise ValueError("Sipariş boş olamaz")
        
        # İş kuralı: Masa müsait olmalı
        if table.is_occupied:
            raise ValueError("Masa dolu")
        
        # Repository ile kaydet
        order.status = 'completed'
        self.order_repo.save(order)
        
        # Masayı doldur
        self.table_repo.set_occupied(table_id, True)
```

#### 3️⃣ **Repositories** (Veri Erişimi)
- Veritabanı CRUD işlemleri
- Query'leri yönetir
- Model'ler ile çalışır

**Örnek:**
```python
class ProductRepository(BaseRepository[Product]):
    def get_by_category(self, category):
        return self.model.query.filter_by(category=category).all()
    
    def get_available_products(self):
        return self.model.query.filter_by(is_available=True).all()
```

#### 4️⃣ **Models** (Veri Yapıları)
- Veritabanı tablolarını temsil eder
- İlişkileri tanımlar
- Sadece veri, hiç logic yok

**Örnek:**
```python
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    # İlişkiler
    order_items = db.relationship('OrderItem', backref='product')
```

### SOLID Prensipleri Uygulaması

#### **S**ingle Responsibility Principle
Her sınıf tek sorumluluğa sahip:
- `ProductService` → Sadece ürün business logic
- `ProductRepository` → Sadece ürün data access
- `ProductValidator` → Sadece ürün validation

#### **O**pen/Closed Principle
Yeni özellikler için kod değiştirilmez, genişletilir:
- Strategy Pattern ile yeni ödeme yöntemleri eklenebilir

#### **L**iskov Substitution Principle
Alt sınıflar üst sınıfın yerine kullanılabilir:
- Tüm Repository'ler `BaseRepository`'den türer

#### **I**nterface Segregation Principle
Her servis sadece ihtiyacı olan metodları içerir:
- Karışık "mega servis" yok

#### **D**ependency Inversion Principle
Yüksek seviye modüller abstraction'a bağımlı:
- Controller → Service → Repository

---

## 💻 Teknoloji Stack

### Backend Framework
- **Flask 2.3.3** - Mikro web framework
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **Flask-WTF** - Form validation
- **Werkzeug** - WSGI utilities ve güvenlik

### Veritabanı
- **SQLite** - Development için dosya bazlı DB

### Raporlama & İletişim
- **ReportLab 4.0.4** - PDF oluşturma
- **OpenPyXL 3.1.2** - Excel export
- **SMTP** - Email gönderimi
- **Pillow 10.0.1** - Resim işleme

### Frontend
- **Bootstrap 5** - Responsive UI framework
- **JavaScript** - İnteraktif özellikler
- **Jinja2** - Template engine

### Güvenlik
- **Bcrypt 4.0.1** - Password hashing
- **Email Validator 2.0.0** - Email doğrulama
- **WTForms CSRF** - Cross-Site Request Forgery koruması

### DevOps
- **Docker & Docker Compose** - Containerization
- **Python Dotenv 1.0.0** - Environment management

---

## 🚀 Kurulum

### 🐳 Docker ile Çalıştırma

Docker kullanarak projeyi kolayca başlatabilirsiniz:

```bash
docker-compose up -d
```

### 💻 Docker olmadan Çalıştırma

```bash
# Çalışma dizinine gidin

# Python sanal ortamı oluşturun
python3 -m venv venv

# Sanal ortamı etkinleştirin
source venv/bin/activate

# pip'i güncelleyin
pip install --upgrade pip

# requirements.txt dosyasından tüm bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python3 app.py
```

---

## ⚙️ Çalışma Mekanizması

### 1. 🔄 İstek Akışı (Request Flow)

```
1. Client → HTTP Request
   │
   ▼
2. Flask Router → Endpoint bulur
   │
   ▼
3. Controller → İsteği yakalar
   │
   ├─► Form Validation (WTForms)
   ├─► Business Validation (Validators)
   │
   ▼
4. Service Layer → Business Logic
   │
   ├─► İş kurallarını uygular
   ├─► Repository'leri kullanır
   ├─► Transaction yönetir
   │
   ▼
5. Repository Layer → Data Access
   │
   ├─► SQL Query'leri oluşturur
   ├─► ORM (SQLAlchemy) kullanır
   │
   ▼
6. Model Layer → Database
   │
   ├─► CRUD işlemleri
   ├─► İlişkisel veriler
   │
   ▼
7. Response → Client'a geri döner
   │
   ├─► JSON (API)
   ├─► HTML (Templates)
   └─► Redirect
```


## 🗄️ Veritabanı Şeması

### Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐
│    Users     │         │    Admins    │
├──────────────┤         ├──────────────┤
│ id (PK)      │         │ id (PK)      │
│ phone*       │         │ email*       │
│ name         │         │ password_hash│
│ email        │         │ name         │
│ created_at   │         │ role         │
└──────┬───────┘         └──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐   N:1   ┌──────────────┐
│    Orders    │◄────────┤    Tables    │
├──────────────┤         ├──────────────┤
│ id (PK)      │         │ id (PK)      │
│ user_id (FK) │         │ name         │
│ table_id (FK)│         │ capacity     │
│ total_amount │         │ is_occupied  │
│ status       │         │ created_at   │
│ created_at   │         └──────────────┘
└──────┬───────┘
       │
       │ 1:N                1:N
       ▼                    │
┌──────────────┐           │
│  OrderItems  │           │
├──────────────┤           │
│ id (PK)      │           │
│ order_id (FK)│           │
│ product_id(FK)◄──────────┘
│ quantity     │           
│ price        │    ┌──────────────┐
│ subtotal     │    │   Products   │
└──────────────┘    ├──────────────┤
                    │ id (PK)      │
┌──────────────┐    │ name         │
│   Payments   │    │ description  │
├──────────────┤    │ price        │
│ id (PK)      │    │ category     │
│ order_id (FK)│    │ image_url    │
│ amount       │    │ is_available │
│ method       │    └──────────────┘
│ status       │
│ created_at   │    ┌──────────────┐
└──────────────┘    │   Contacts   │
                    ├──────────────┤
┌──────────────┐    │ id (PK)      │
│     OTP      │    │ name         │
├──────────────┤    │ email        │
│ id (PK)      │    │ type         │
│ email        │    │ message      │
│ code         │    │ rating       │
│ expires_at   │    │ reply        │
│ used         │    │ created_at   │
└──────────────┘    └──────────────┘
```

### Tablo Detayları

#### **Users** (Müşteriler)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    phone VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

#### **Products** (Ürünler)
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    category VARCHAR(50) NOT NULL,  -- 'yemek', 'tatlı', 'içecek', 'salata'
    image_url VARCHAR(500),
    is_available BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### **Orders** (Siparişler)
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    table_id INTEGER,
    total_amount FLOAT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'completed', 'payment_pending', 'paid'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (table_id) REFERENCES tables(id)
);
```

#### **Payments** (Ödemeler)
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE,
    amount FLOAT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,  -- 'cash', 'card'
    status VARCHAR(50) DEFAULT 'completed',
    transaction_id VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

### Sipariş Durumu Akışı

```
┌─────────┐   place_order   ┌───────────┐   complete   ┌─────────────────┐
│ PENDING ├────────────────►│ COMPLETED ├─────────────►│ PAYMENT_PENDING │
└─────────┘                 └───────────┘              └────────┬────────┘
                                                                 │
                                                    process_payment
                                                                 │
                                                                 ▼
                                                        ┌────────────┐
                                                        │    PAID    │
                                                        └────────────┘
```
---

## 📊 Proje İstatistikleri

- **Toplam Dosya**: 100+
- **Python Kod Satırı**: 5000+
- **HTML Template**: 30+
- **Model Sayısı**: 8
- **Service Sayısı**: 9
- **Controller Sayısı**: 4
- **Endpoint Sayısı**: 60+


## 🙏 Teşekkürler

<div align="center">

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐**

**🍽️ Afiyet Olsun! 🍽️**

Made with ❤️ by [Kevser ÖZCAN][Elif KOŞAR][Bahriye İŞGÖR][Rümeysa YURTSEVER][İrem Naz Kaya][Feray Yaren TURASAY]


<img width="1890" height="945" alt="463389088-0ee31e1e-47c5-4103-89f0-3174b6843531" src="https://github.com/user-attachments/assets/f0f0c4e6-7252-4485-95a1-54c62ca23ed7" />

</div>

