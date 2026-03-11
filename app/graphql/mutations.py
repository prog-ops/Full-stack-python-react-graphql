import strawberry
from strawberry.file_uploads import Upload
import csv
import io
from typing import List
from datetime import datetime
from app.graphql.types import ImportSummary


@strawberry.type
class Mutation:
    @strawberry.mutation
    def import_transactions(self, file: Upload) -> ImportSummary:
        # Read CSV file content
        content = file.file.read().decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(content))

        total_rows = 0
        accepted_rows = 0
        rejected_rows = 0
        validation_errors = []

        # In real app, we will open db session (SQLAlchemy) here.
        # db = SessionLocal()

        for row_number, row in enumerate(csv_reader, start=1):
            total_rows += 1
            try:
                # 1. Mandatory column Validation
                sku = row.get("sku")
                warehouse = row.get("warehouse")
                tx_type_str = row.get("transaction_type")
                quantity_str = row.get("quantity")

                if not all([sku, warehouse, tx_type_str, quantity_str]):
                    raise ValueError("Missing required fields (sku, warehouse, transaction_type, quantity).")

                # 2. Data type Validation
                quantity = int(quantity_str)
                if quantity < 0 and tx_type_str != "adjustment":
                    raise ValueError("Quantity cannot be negative unless it's an adjustment.")

                # 3. Transaction Type Validasi
                valid_types = ["restock", "sale", "adjustment"]
                if tx_type_str not in valid_types:
                    raise ValueError(f"Invalid transaction_type: {tx_type_str}. Must be one of {valid_types}.")

                # --- Business Logic (DB Simulation) ---
                # db_item = db.query(InventoryItemDB).filter(InventoryItemDB.sku == sku).first()
                # if not db_item:
                #     raise ValueError(f"SKU {sku} not found in inventory.")

                # Update quantity by transaction type
                # if tx_type_str == "restock":
                #     db_item.quantity_on_hand += quantity
                # elif tx_type_str == "sale":
                #     if db_item.quantity_on_hand < quantity:
                #         raise ValueError(f"Insufficient stock for sale. Current: {db_item.quantity_on_hand}")
                #     db_item.quantity_on_hand -= quantity
                # elif tx_type_str == "adjustment":
                #     db_item.quantity_on_hand = quantity  # Asumsi: adjustment menetapkan nilai absolut

                # Record transaction to TransactionDB table
                # new_tx = TransactionDB(item_sku=sku, warehouse=warehouse, ...)
                # db.add(new_tx)

                accepted_rows += 1

            except Exception as e:
                rejected_rows += 1
                validation_errors.append(f"Row {row_number} (SKU: {row.get('sku', 'Unknown')}): {str(e)}")

        # db.commit() # Save to db

        return ImportSummary(
            total_rows=total_rows,
            accepted_rows=accepted_rows,
            rejected_rows=rejected_rows,
            validation_errors=validation_errors
        )