import sys
import os
# Make sure project root is on sys.path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from extensions import db
from models import Table, Order

app = create_app()
with app.app_context():
    ACTIVE = ['pending', 'completed', 'payment_pending']
    stale = []
    for t in Table.query.filter_by(is_occupied=True).all():
        active_count = Order.query.filter(Order.table_id == t.id, Order.status.in_(ACTIVE)).count()
        if active_count == 0:
            stale.append((t.id, t.name))
    if not stale:
        print('No stale occupied tables found.')
    else:
        print('Stale occupied tables:')
        for sid, name in stale:
            print(f'- id={sid} name={name}')
