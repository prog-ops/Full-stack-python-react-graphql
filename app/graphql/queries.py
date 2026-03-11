import strawberry
from typing import List, Optional
from strawberry.types import Info
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models import InventoryItemDB
from app.graphql.types import InventoryItem


@strawberry.type
class Query:
    @strawberry.field
    def items(
            self,
            info: Info,
            search: Optional[str] = None,
            category: Optional[str] = None,
            warehouse: Optional[str] = None,
            stock_status: Optional[str] = None,
            sort_by: Optional[str] = None,
            sort_desc: Optional[bool] = False,
            skip: Optional[int] = 0,
            limit: Optional[int] = 100,
    ) -> List[InventoryItem]:

        # Take db session from context
        db: Session = info.context["db"]

        # Build base query
        query = db.query(InventoryItemDB)

        # Apply filter when parameter is given
        if search:
            query = query.filter(
                (InventoryItemDB.name.ilike(f"%{search}%")) |
                (InventoryItemDB.sku.ilike(f"%{search}%"))
            )
        if category:
            query = query.filter(InventoryItemDB.category == category)
        if warehouse:
            query = query.filter(InventoryItemDB.warehouse == warehouse)
            
        if stock_status:
            if stock_status == "Out of Stock":
                query = query.filter(InventoryItemDB.quantity_on_hand <= 0)
            elif stock_status == "Low Stock":
                query = query.filter(InventoryItemDB.quantity_on_hand > 0, 
                                     InventoryItemDB.quantity_on_hand <= InventoryItemDB.reorder_threshold)
            elif stock_status == "In Stock":
                query = query.filter(InventoryItemDB.quantity_on_hand > InventoryItemDB.reorder_threshold)

        # Apply Sorting
        if sort_by:
            sort_column = None
            if sort_by == "name":
                sort_column = InventoryItemDB.name
            elif sort_by == "quantity":
                sort_column = InventoryItemDB.quantity_on_hand
            elif sort_by == "last_updated":
                sort_column = InventoryItemDB.last_updated
            
            if sort_column is not None:
                if sort_desc:
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))

        # Apply Pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        db_items = query.all()

        # Map db result GraphQL type
        return [
            InventoryItem(
                item_id=str(item.item_id),
                sku=item.sku,
                name=item.name,
                category=item.category,
                warehouse=item.warehouse,
                quantity_on_hand=item.quantity_on_hand,
                reorder_threshold=item.reorder_threshold,
                last_updated=item.last_updated.isoformat()
            ) for item in db_items
        ]