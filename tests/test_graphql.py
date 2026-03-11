import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import io

from main import app
from app.database import Base, get_db
from app.models import InventoryItemDB

from sqlalchemy.pool import StaticPool

# 1. Setup In-Memory Database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override dependency get_db so FastAPI can use this db test
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# Fixture to recreate table every time test is run
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# 2. TEST: Stock Status logic and Query Resolver
def test_stock_status_logic():
    # Setup first data in db test
    db = TestingSessionLocal()
    db.add_all([
        InventoryItemDB(sku="OUT01", name="Item Out", category="A", warehouse="W1", quantity_on_hand=0,
                        reorder_threshold=5),
        InventoryItemDB(sku="LOW01", name="Item Low", category="A", warehouse="W1", quantity_on_hand=5,
                        reorder_threshold=5),
        InventoryItemDB(sku="IN01", name="Item In", category="A", warehouse="W1", quantity_on_hand=10,
                        reorder_threshold=5),
    ])
    db.commit()
    db.close()

    # GraphQL Query Execution
    query = """
    query {
      items {
        sku
        stockStatus
      }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200

    response_json = response.json()

    # If GraphQL is error, the test will fail and shows error
    assert "errors" not in response_json, f"GraphQL Error: {response_json.get('errors')}"

    data = response_json["data"]["items"]

    # Validation logic by assumption of:
    # 0 = Out of Stock, qty <= threshold = Low Stock, qty > threshold = In Stock
    for item in data:
        if item["sku"] == "OUT01":
            assert item["stockStatus"] == "Out of Stock"
        elif item["sku"] == "LOW01":
            assert item["stockStatus"] == "Low Stock"
        elif item["sku"] == "IN01":
            assert item["stockStatus"] == "In Stock"


# 3. TEST: Import CSV (Mutation) Validation Logic
def test_import_validation_logic():
    # Create CSV file in memory that contains valid and invalid data (negative quantity for restock)
    csv_content = """sku,warehouse,transaction_type,quantity
SKU01,W1,restock,10
SKU02,W1,restock,-5
SKU03,W1,invalid_type,5
"""
    # Prepare payload multipart/form-data for Strawberry GraphQL file upload
    query = """
    mutation($file: Upload!) {
      importTransactions(file: $file) {
        totalRows
        acceptedRows
        rejectedRows
        validationErrors
      }
    }
    """

    # Change string to bytes
    csv_bytes = csv_content.encode("utf-8")

    # Strawberry has specific format for file upload via REST/Multipart
    files = {
        '0': ('test.csv', io.BytesIO(csv_bytes), 'text/csv')
    }
    data = {
        'operations': '{"query": "mutation($file: Upload!) { importTransactions(file: $file) { totalRows acceptedRows rejectedRows validationErrors } }", "variables": {"file": null}}',
        'map': '{"0": ["variables.file"]}'
    }

    response = client.post("/graphql", data=data, files=files)
    assert response.status_code == 200

    result = response.json()["data"]["importTransactions"]

    # Assertions
    assert result["totalRows"] == 3
    assert result["acceptedRows"] == 1  # Only first row is valid
    assert result["rejectedRows"] == 2

    # Check error message whether it matches the validation
    errors = result["validationErrors"]
    assert any("Quantity cannot be negative" in err for err in errors)
    assert any("Invalid transaction_type" in err for err in errors)