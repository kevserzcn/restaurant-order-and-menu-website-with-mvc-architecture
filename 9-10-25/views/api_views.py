"""
API Views - MVC View Layer
Handles all API related view logic
"""

from flask import jsonify, request
from models import Product, Order, Table

class ApiViews:
    """API view methods"""
    
    @staticmethod
    def render_products(products):
        """Render products as JSON"""
        return jsonify([product.to_dict() for product in products])
    
    @staticmethod
    def render_products_by_category(products):
        """Render products by category as JSON"""
        return jsonify([product.to_dict() for product in products])
    
    @staticmethod
    def render_tables(tables):
        """Render tables as JSON"""
        return jsonify([table.to_dict() for table in tables])
    
    @staticmethod
    def render_order(order):
        """Render order as JSON"""
        return jsonify(order.to_dict())
    
    @staticmethod
    def render_search_results(products):
        """Render search results as JSON"""
        return jsonify([product.to_dict() for product in products])
    
    @staticmethod
    def render_error(message, status_code=400):
        """Render error response"""
        return jsonify({'error': message}), status_code
    
    @staticmethod
    def render_success(message, data=None):
        """Render success response"""
        response = {'success': True, 'message': message}
        if data:
            response['data'] = data
        return jsonify(response)
