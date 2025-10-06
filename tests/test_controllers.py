import unittest
from app import create_app
from extensions import db
from models import User, Admin, Product, Order, Table
from flask import url_for

class TestControllers(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_page(self):
        """Test index page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Restoran Menü Sistemi', response.data)

    def test_user_login_page(self):
        """Test user login page loads"""
        response = self.client.get('/auth/user/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Müşteri Girişi', response.data)

    def test_user_register_page(self):
        """Test user register page loads"""
        response = self.client.get('/auth/user/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Müşteri Kayıt', response.data)

    def test_admin_login_page(self):
        """Test admin login page loads"""
        response = self.client.get('/auth/admin/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Girişi', response.data)

    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/auth/user/register', data={
            'phone': '05551234567',
            'name': 'Test User'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Check if user was created
        user = User.query.filter_by(phone='05551234567').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'Test User')

    def test_user_login(self):
        """Test user login"""
        # Create a test user
        user = User(phone='05551234567', name='Test User')
        db.session.add(user)
        db.session.commit()
        
        response = self.client.post('/auth/user/login', data={
            'phone': '05551234567',
            'name': 'Test User'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_admin_login(self):
        """Test admin login"""
        # Create a test admin
        admin = Admin(email='admin@test.com', password='password123', name='Admin User')
        db.session.add(admin)
        db.session.commit()
        
        response = self.client.post('/auth/admin/login', data={
            'email': 'admin@test.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_user_dashboard_requires_login(self):
        """Test user dashboard requires login"""
        response = self.client.get('/user/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_admin_dashboard_requires_login(self):
        """Test admin dashboard requires login"""
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_add_product_requires_admin(self):
        """Test add product requires admin login"""
        response = self.client.get('/admin/products/add')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_api_products(self):
        """Test API products endpoint"""
        # Create test products
        product1 = Product(name='Product 1', price=25.50, category='yemek')
        product2 = Product(name='Product 2', price=15.00, category='içecek')
        db.session.add_all([product1, product2])
        db.session.commit()
        
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product 1', response.data)
        self.assertIn(b'Product 2', response.data)

    def test_api_products_by_category(self):
        """Test API products by category"""
        # Create test products
        product1 = Product(name='Yemek Product', price=25.50, category='yemek')
        product2 = Product(name='İçecek Product', price=15.00, category='içecek')
        db.session.add_all([product1, product2])
        db.session.commit()
        
        response = self.client.get('/api/products/yemek')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Yemek Product', response.data)
        self.assertNotIn(b'İçecek Product', response.data)

    def test_api_search(self):
        """Test API search functionality"""
        # Create test products
        product1 = Product(name='Pizza Margherita', price=25.50, category='yemek')
        product2 = Product(name='Coca Cola', price=5.00, category='içecek')
        db.session.add_all([product1, product2])
        db.session.commit()
        
        response = self.client.get('/api/search?q=pizza')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pizza Margherita', response.data)
        self.assertNotIn(b'Coca Cola', response.data)

if __name__ == '__main__':
    unittest.main()
