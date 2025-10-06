import unittest
from app import create_app
from extensions import db
from models import User, Admin, Product, Order, OrderItem, Table, Payment

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test user creation"""
        user = User(phone="05551234567", name="Test User")
        db.session.add(user)
        db.session.commit()
        
        self.assertEqual(user.phone, "05551234567")
        self.assertEqual(user.name, "Test User")
        self.assertTrue(user.check_password("Test User"))

    def test_admin_creation(self):
        """Test admin creation"""
        admin = Admin(email="admin@test.com", password="password123", name="Admin User")
        db.session.add(admin)
        db.session.commit()
        
        self.assertEqual(admin.email, "admin@test.com")
        self.assertEqual(admin.name, "Admin User")
        self.assertTrue(admin.check_password("password123"))

    def test_product_creation(self):
        """Test product creation"""
        product = Product(
            name="Test Product",
            description="Test Description",
            price=25.50,
            category="yemek"
        )
        db.session.add(product)
        db.session.commit()
        
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.price, 25.50)
        self.assertEqual(product.category, "yemek")

    def test_table_creation(self):
        """Test table creation"""
        table = Table(table_number=1, capacity=4, waiter_name="Test Waiter")
        db.session.add(table)
        db.session.commit()
        
        self.assertEqual(table.table_number, 1)
        self.assertEqual(table.capacity, 4)
        self.assertEqual(table.waiter_name, "Test Waiter")

    def test_order_creation(self):
        """Test order creation"""
        user = User(phone="05551234567", name="Test User")
        db.session.add(user)
        db.session.flush()
        
        order = Order(user_id=user.id)
        db.session.add(order)
        db.session.commit()
        
        self.assertEqual(order.user_id, user.id)
        self.assertEqual(order.status, "pending")

    def test_order_item_creation(self):
        """Test order item creation"""
        user = User(phone="05551234567", name="Test User")
        product = Product(name="Test Product", price=25.50, category="yemek")
        db.session.add_all([user, product])
        db.session.flush()
        
        order = Order(user_id=user.id)
        db.session.add(order)
        db.session.flush()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            price=25.50
        )
        db.session.add(order_item)
        db.session.commit()
        
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, 25.50)

    def test_payment_creation(self):
        """Test payment creation"""
        user = User(phone="05551234567", name="Test User")
        db.session.add(user)
        db.session.flush()
        
        order = Order(user_id=user.id)
        db.session.add(order)
        db.session.flush()
        
        payment = Payment(
            order_id=order.id,
            amount=50.00,
            payment_method="cash",
            status="completed"
        )
        db.session.add(payment)
        db.session.commit()
        
        self.assertEqual(payment.amount, 50.00)
        self.assertEqual(payment.payment_method, "cash")
        self.assertEqual(payment.status, "completed")

if __name__ == '__main__':
    unittest.main()
