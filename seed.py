from app.database import SessionLocal, init_db
from app.models import InventoryItemDB

'''
A seeder to insert data
'''
def seed_data():
    # Make sure the table is already created
    init_db()

    db = SessionLocal()

    # Check whether db is empty or not
    if db.query(InventoryItemDB).count() == 0:
        print("Database kosong. Menambahkan data dummy...")

        dummy_items = [
            InventoryItemDB(sku="SKU001", name="Laptop Pro", category="Electronics", warehouse="Jakarta",
                            quantity_on_hand=50, reorder_threshold=10),
            InventoryItemDB(sku="SKU002", name="Mechanical Keyboard", category="Electronics", warehouse="Jakarta",
                            quantity_on_hand=5, reorder_threshold=10),  # Akan jadi Low Stock
            InventoryItemDB(sku="SKU003", name="Ergonomic Chair", category="Furniture", warehouse="Bandung",
                            quantity_on_hand=0, reorder_threshold=5),  # Akan jadi Out of Stock
            InventoryItemDB(sku="SKU004", name="Wireless Mouse", category="Electronics", warehouse="Surabaya",
                            quantity_on_hand=15, reorder_threshold=20),  # Akan jadi Low Stock
        ]

        db.add_all(dummy_items)
        db.commit()
        print("Data dummy berhasil ditambahkan secara permanen ke inventory.db!")
    else:
        print("Database sudah berisi data. Tidak ada data baru yang ditambahkan.")

    db.close()


if __name__ == "__main__":
    seed_data()