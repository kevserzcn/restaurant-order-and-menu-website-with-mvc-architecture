"""
Forms Paketi
============
Uygulamada kullanılan tüm WTForms form tanımlarını içerir.

Modüller:
- auth_forms: Giriş ve kayıt formları (UserLoginForm, UserRegisterForm, AdminLoginForm)
- product_forms: Ürün yönetimi formları (ProductForm)
- table_forms: Masa yönetimi formları (TableForm)
- order_forms: Sipariş yönetimi formları (OrderItemForm)
"""

from forms.auth_forms import UserLoginForm, UserRegisterForm, AdminLoginForm, ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm
from forms.product_forms import ProductForm
from forms.table_forms import TableForm
from forms.order_forms import OrderItemForm
from forms.contact_forms import ContactForm, ReviewForm, ReplyForm

__all__ = [
    'UserLoginForm',
    'UserRegisterForm', 
    'AdminLoginForm',
    'ForgotPasswordForm',
    'VerifyOTPForm',
    'ResetPasswordForm',
    'ProductForm',
    'TableForm',
    'OrderItemForm',
    'ContactForm',
    'ReviewForm',
    'ReplyForm'
]
