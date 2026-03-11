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
    # Assumption for Stock Status Logic:
    # 1. 'Out of Stock' : If quantity_on_hand is 0 or less, the item simply doesn't exist to sell.
    # 2. 'Low Stock'    : If quantity_on_hand is more than 0 but still below or equal to the reorder threshold. 
    #                     It's an indicator that we need to restock before it becomes 'Out of Stock'.
    # 3. 'In Stock'     : If quantity_on_hand is strictly greater than the reorder threshold, 
    #                     the supply is in a healthy, sufficient state.
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