from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# Register a global user loader for Flask-Login
@login_manager.user_loader
def _load_user(user_id):
	try:
		uid = int(user_id)
	except (TypeError, ValueError):
		return None
	# Import here to avoid circular imports
	try:
		from models import User, Admin
	except Exception:
		return None
	user = None
	try:
		user = User.query.get(uid)
	except Exception:
		user = None
	if user:
		return user
	try:
		return Admin.query.get(uid)
	except Exception:
		return None
