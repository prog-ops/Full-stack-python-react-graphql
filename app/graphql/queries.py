import strawberry
from typing import List, Optional
from strawberry.types import Info
from sqlalchemy.orm import Session
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
            warehouse: Optional[str] = None
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