import strawberry
from typing import List

'''
Inventory Item Type
'''
@strawberry.type
class InventoryItem:
    item_id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_threshold: int
    last_updated: str

    # Dynamic field for Stock Status
    @strawberry.field
    def stock_status(self) -> str:
        if self.quantity_on_hand <= 0:
            return "Out of Stock"
        elif self.quantity_on_hand <= self.reorder_threshold:
            return "Low Stock"
        return "In Stock"

'''
Import Summary Type
'''
@strawberry.type
class ImportSummary:
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    validation_errors: List[str]