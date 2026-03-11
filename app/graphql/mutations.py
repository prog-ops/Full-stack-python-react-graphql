import strawberry
from strawberry.file_uploads import Upload
import csv
import io
from typing import List
from datetime import datetime
from app.graphql.types import ImportSummary


from strawberry.types import Info
from app.models import InventoryItemDB, TransactionDB
import traceback


@strawberry.type
class Mutation:
    @strawberry.mutation
    def import_transactions(self, info: Info, file: Upload) -> ImportSummary:
        # Read CSV file content
        content = file.file.read().decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(content))

        total_rows = 0
        accepted_rows = 0
        rejected_rows = 0
        validation_errors = []

        # Use Partial Success strategy: If a few rows are invalid, we still process the valid rows.
        # This is because in bulk operations, it is more user-friendly to accept what is correct 
        # and give a report of what failed, instead of discarding 900 valid rows due to 1 bad row.
        db = info.context["db"]

        try:
            for row_number, row in enumerate(csv_reader, start=1):
                total_rows += 1
                try:
                    # 1. Mandatory column Validation (now includes 'timestamp' from requirements)
                    sku = row.get("sku")
                    warehouse = row.get("warehouse")
                    tx_type_str = row.get("transaction_type")
                    quantity_str = row.get("quantity")
                    timestamp_str = row.get("timestamp")

                    if not all([sku, warehouse, tx_type_str, quantity_str]):
                        raise ValueError("Missing required fields (sku, warehouse, transaction_type, quantity).")

                    # 2. Data type Validation
                    quantity = int(quantity_str)
                    if quantity < 0 and tx_type_str != "adjustment":
                        raise ValueError("Quantity cannot be negative unless it's an adjustment.")

                    # Validate timestamp if provided
                    tx_timestamp = datetime.utcnow()
                    if timestamp_str:
                        try:
                            # Try parsing ISO 8601 format
                            tx_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except ValueError:
                            # fallback to default format if not ISO
                            pass

                    # 3. Transaction Type Validation
                    valid_types = ["restock", "sale", "adjustment"]
                    if tx_type_str not in valid_types:
                        raise ValueError(f"Invalid transaction_type: {tx_type_str}. Must be one of {valid_types}.")

                    # --- Business Logic (Real Database Operation) ---
                    db_item = db.query(InventoryItemDB).filter(InventoryItemDB.sku == sku).first()
                    if not db_item:
                        raise ValueError(f"SKU {sku} not found in inventory.")

                    # Update quantity by transaction type
                    if tx_type_str == "restock":
                        db_item.quantity_on_hand += quantity
                    elif tx_type_str == "sale":
                        if db_item.quantity_on_hand < quantity:
                            raise ValueError(f"Insufficient stock for sale. Current: {db_item.quantity_on_hand}, Requested: {quantity}")
                        db_item.quantity_on_hand -= quantity
                    elif tx_type_str == "adjustment":
                        # Assumption: adjustment sets the absolute value
                        db_item.quantity_on_hand = quantity  

                    # Record transaction to TransactionDB table
                    new_tx = TransactionDB(
                        item_sku=sku, 
                        warehouse=warehouse, 
                        transaction_type=tx_type_str,
                        quantity=quantity,
                        timestamp=tx_timestamp
                    )
                    db.add(new_tx)

                    # Only commit periodically or at the end to improve performance, but here 
                    # we do flush to catch DB constraints early if needed
                    db.flush() 

                    accepted_rows += 1

                except Exception as e:
                    # We continue the loop because we use "Partial Success" approach
                    rejected_rows += 1
                    validation_errors.append(f"Row {row_number} (SKU: {row.get('sku', 'Unknown')}): {str(e)}")

            db.commit() # Commit all valid entries at the end
            
        except Exception as global_e:
            db.rollback()
            return ImportSummary(
                total_rows=total_rows,
                accepted_rows=0,
                rejected_rows=total_rows,
                validation_errors=[f"Critical error processing CSV: {str(global_e)}"]
            )

        return ImportSummary(
            total_rows=total_rows,
            accepted_rows=accepted_rows,
            rejected_rows=rejected_rows,
            validation_errors=validation_errors
        )