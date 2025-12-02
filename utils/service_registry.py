from typing import Dict, Type, Any


class ServiceRegistry:
    
    _instances: Dict[Type, Any] = {}
    
    @classmethod
    def get_service(cls, service_class: Type) -> Any:
        if service_class not in cls._instances:
            cls._instances[service_class] = service_class()
        return cls._instances[service_class]
    
    @classmethod
    def clear(cls):
        cls._instances.clear()


def get_order_service():
    from services.order_service import OrderService
    return ServiceRegistry.get_service(OrderService)


def get_product_service():
    from services.product_service import ProductService
    return ServiceRegistry.get_service(ProductService)


def get_table_service():
    from services.table_service import TableService
    return ServiceRegistry.get_service(TableService)


def get_payment_service():
    from services.payment_service import PaymentService
    return ServiceRegistry.get_service(PaymentService)


def get_contact_service():
    from services.contact_service import ContactService
    return ServiceRegistry.get_service(ContactService)