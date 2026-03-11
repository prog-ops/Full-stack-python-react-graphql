from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum
import uuid

'''
SQLAlchemy ORM
'''

Base = declarative_base()

# Enum for transaction type
class TransactionType(enum.Enum):
    restock = "restock"
    sale = "sale"
    adjustment = "adjustment"

class InventoryItemDB(Base):
    __tablename__ = "inventory_items"

    item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, index=True)
    warehouse = Column(String, index=True)
    quantity_on_hand = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relation to transaction (Optional, but good for data integrity)
    transactions = relationship("TransactionDB", back_populates="item")

class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_sku = Column(String, ForeignKey("inventory_items.sku"), nullable=False)
    warehouse = Column(String, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    item = relationship("InventoryItemDB", back_populates="transactions")