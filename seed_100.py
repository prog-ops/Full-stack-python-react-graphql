from app.database import SessionLocal, init_db
from app.models import InventoryItemDB
import random

def seed_100_data():
    init_db()
    db = SessionLocal()
    
    categories = ["Electronics", "Furniture", "Clothing", "Tools", "Office Supplies"]
    warehouses = ["Jakarta", "Bandung", "Surabaya", "W1", "W2"]
    
    items = []
    # Start counting after current records to avoid SKU overlap easily
    base_sku = 100 
    
    # Just in case, find highest SKU starting with SKU
    existing_items = db.query(InventoryItemDB).all()
    for item in existing_items:
        if item.sku.startswith("SKU"):
            try:
                num = int(item.sku[3:])
                if num >= base_sku:
                    base_sku = num + 1
            except ValueError:
                pass
    
    for i in range(100):
        qty = random.randint(0, 100)
        threshold = random.randint(5, 20)
        items.append(
            InventoryItemDB(
                sku=f"SKU{base_sku + i:03d}",
                name=f"Generated Item {base_sku + i}",
                category=random.choice(categories),
                warehouse=random.choice(warehouses),
                quantity_on_hand=qty,
                reorder_threshold=threshold
            )
        )
        
    db.add_all(items)
    db.commit()
    db.close()
    
    print("100 generated items added successfully!")

if __name__ == "__main__":
    seed_100_data()
