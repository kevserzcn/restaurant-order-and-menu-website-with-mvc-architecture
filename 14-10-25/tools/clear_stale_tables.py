import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import Table, Order

app = create_app()
with app.app_context():
    ACTIVE = ['pending', 'completed', 'payment_pending']
    # target table names to clear (from your report)
    target_names = ["Elf's", 'Theo James', 'Niko', 'Yalı']
    changed = []
    for name in target_names:
        table = Table.query.filter_by(name=name).first()
        if not table:
            print(f"Table not found: {name}")
            continue
        active_count = Order.query.filter(Order.table_id == table.id, Order.status.in_(ACTIVE)).count()
        print(f"Table: {table.id} {table.name} - is_occupied={table.is_occupied} - active_orders={active_count}")
        if table.is_occupied and active_count == 0:
            table.is_occupied = False
            changed.append((table.id, table.name))
    if changed:
        from extensions import db
        db.session.commit()
        print('\nCleared occupied flag for:')
        for tid, tname in changed:
            print(f'- id={tid} name={tname}')
    else:
        print('\nNo tables needed clearing.')
