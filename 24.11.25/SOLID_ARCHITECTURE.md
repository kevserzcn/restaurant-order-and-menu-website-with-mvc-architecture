# SOLID Mimarisi - Restoran Yönetim Sistemi

## 📐 Mimari Genel Bakış

Bu proje **SOLID prensipleri** doğrultusunda yeniden yapılandırılmıştır.

```
┌─────────────┐
│  Controller │  → HTTP isteklerini işler
└──────┬──────┘
       │ uses
┌──────▼──────┐
│   Service   │  → Business logic
└──────┬──────┘
       │ uses
┌──────▼──────┐
│ Repository  │  → Veritabanı işlemleri
└──────┬──────┘
       │ uses
┌──────▼──────┐
│    Model    │  → ORM tanımları
└─────────────┘
```

## 🎯 SOLID Prensipleri Uygulaması

### 1. **S**ingle Responsibility Principle (SRP)
✅ Her sınıf tek bir sorumluluğa sahip

**Örnekler:**
- `ProductRepository` → Sadece ürün CRUD işlemleri
- `OrderService` → Sadece sipariş business logic
- `ProductValidator` → Sadece ürün validasyonu

### 2. **O**pen/Closed Principle (OCP)
✅ Yeni özellikler için kod değiştirilmez, genişletilir

**Örnek - Payment Strategy:**
```python
# Yeni ödeme yöntemi eklemek için:
class CryptoPaymentStrategy(PaymentStrategy):
    def process(self, amount, **kwargs):
        # Kripto para ödeme işlemi
        pass
```

### 3. **L**iskov Substitution Principle (LSP)
✅ Alt sınıflar üst sınıfın yerine kullanılabilir

**Örnek:**
```python
strategy: PaymentStrategy = CashPaymentStrategy()
strategy: PaymentStrategy = CardPaymentStrategy()
# Her ikisi de aynı interface'i kullanır
```

### 4. **I**nterface Segregation Principle (ISP)
✅ Her servis sadece ihtiyacı olan metodları içerir

**Örnek:**
- `ProductService` → Sadece ürün işlemleri
- `OrderService` → Sadece sipariş işlemleri
- Karışık "mega servis" yok!

### 5. **D**ependency Inversion Principle (DIP)
✅ Yüksek seviye modüller düşük seviyeye bağımlı değil

**Örnek:**
```python
# Controller → Service → Repository → Model
# Her katman abstraction'a bağımlı
```

## 📁 Proje Yapısı

```
project/
├── models/              # ORM tanımları (Sadece veri yapısı)
│   ├── user.py
│   ├── product.py
│   ├── order.py
│   ├── table.py
│   └── payment.py
│
├── repositories/        # Veritabanı işlemleri (CRUD)
│   ├── base_repository.py
│   ├── product_repository.py
│   ├── order_repository.py
│   ├── table_repository.py
│   ├── user_repository.py
│   └── payment_repository.py
│
├── business/           # Business logic
│   ├── product_service.py
│   ├── order_service.py
│   ├── table_service.py
│   ├── payment_service.py
│   └── payment_strategies/
│       ├── payment_strategy.py
│       ├── cash_payment.py
│       ├── card_payment.py
│       └── mobile_payment.py
│
├── validators/         # Business validation
│   ├── product_validator.py
│   ├── order_validator.py
│   ├── payment_validator.py
│   └── user_validator.py
│
└── controllers/        # HTTP request handling
    ├── admin_controller.py
    ├── user_controller.py
    └── auth_controller.py
```

## 🔄 Katmanlar Arası İlişki

### Örnek: Ürün Ekleme İşlemi

```python
# 1. Controller (HTTP isteği alır)
@admin_bp.route('/products/add', methods=['POST'])
def add_product():
    data = request.form
    
    # 2. Validator (İş kurallarını kontrol eder)
    is_valid, errors = ProductValidator.validate_product(
        data['name'], 
        float(data['price']), 
        data['category']
    )
    
    if not is_valid:
        return jsonify({'errors': errors}), 400
    
    # 3. Service (Business logic)
    product_service = ProductService()
    product = product_service.create_product(
        name=data['name'],
        price=float(data['price']),
        category=data['category']
    )
    
    return jsonify({'success': True, 'product': product.id})

# ProductService (business/product_service.py)
class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()  # Repository'yi kullanır
    
    def create_product(self, name, price, category):
        # İsim kontrolü (business logic)
        if self.product_repo.get_by_name(name):
            raise ValueError("Bu ürün adı zaten mevcut")
        
        # Repository'ye kayıt
        return self.product_repo.create(
            name=name,
            price=price,
            category=category
        )

# ProductRepository (repositories/product_repository.py)
class ProductRepository(BaseRepository[Product]):
    def create(self, **kwargs):
        product = Product(**kwargs)
        db.session.add(product)
        db.session.commit()
        return product
```

## ✨ Avantajlar

### 1. **Test Edilebilirlik**
```python
# Mock repository ile test
class MockProductRepository:
    def get_by_id(self, id):
        return Product(id=1, name="Test")

service = ProductService()
service.product_repo = MockProductRepository()
# Gerçek veritabanına ihtiyaç yok!
```

### 2. **Bakım Kolaylığı**
- Her dosya tek bir sorumluluğa sahip
- Hata ayıklamak kolay
- Kod tekrarı yok

### 3. **Genişletilebilirlik**
- Yeni ödeme yöntemi → Yeni strategy sınıfı ekle
- Yeni validasyon → Validator'a ekle
- Veritabanı değişikliği → Sadece repository değişir

### 4. **Kod Kalitesi**
- Clean Code
- SOLID Principles
- Design Patterns (Strategy, Repository)

## 🚀 Kullanım Örnekleri

### Repository Kullanımı
```python
# Ürün repository
product_repo = ProductRepository()
product = product_repo.get_by_id(1)
products = product_repo.get_by_category('yemek')
available = product_repo.get_available_products()
```

### Service Kullanımı
```python
# Sipariş servisi
order_service = OrderService()
order = order_service.create_order(user_id=1, table_id=5)
order_service.add_item_to_order(order.id, product_id=10, quantity=2, price=50.0)
order_service.place_order(order.id, table_id=5)
```

### Payment Strategy Kullanımı
```python
# Ödeme işlemi
payment_context = PaymentContext()

# Nakit ödeme
result = payment_context.process_payment('cash', 100.0)

# Kart ödeme
result = payment_context.process_payment('card', 100.0, card_number='1234567890123456')

# Mobil ödeme
result = payment_context.process_payment('mobile', 100.0, phone_number='5551234567')
```

### Validator Kullanımı
```python
# Ürün validasyonu
is_valid, errors = ProductValidator.validate_product(
    name="Adana Kebap",
    price=120.50,
    category="yemek"
)

if not is_valid:
    print("Hatalar:", errors)
```

## 📊 Önce ve Sonra Karşılaştırma

### ❌ Önce (SOLID ihlali)
```python
# Controller içinde her şey karışık
@admin_bp.route('/products/add')
def add_product():
    # Validation
    if float(request.form['price']) <= 0:
        flash('Hata!')
    
    # Database
    product = Product(...)
    db.session.add(product)
    db.session.commit()
    
    # Business logic
    if Product.query.filter_by(name=...).first():
        flash('Hata!')
```

### ✅ Sonra (SOLID uyumlu)
```python
# Her şey ayrı katmanlarda
@admin_bp.route('/products/add')
def add_product():
    # Validation
    is_valid, errors = ProductValidator.validate_product(...)
    
    # Business logic
    product_service = ProductService()
    product = product_service.create_product(...)
```

## 🎓 Öğrenilen Design Patterns

1. **Repository Pattern** - Veri erişimi soyutlaması
2. **Strategy Pattern** - Ödeme yöntemleri
3. **Service Layer Pattern** - Business logic katmanı
4. **Dependency Injection** - Loose coupling

---

**Sonuç:** Proje artık SOLID prensiplerine uygun, test edilebilir, bakımı kolay ve genişletilebilir! 🎉
