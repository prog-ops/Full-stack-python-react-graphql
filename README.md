# Enterprise Inventory - FastAPI Backend

This is the backend server for a Full Stack Developer Technical Assessment, functioning as an Enterprise Inventory Management System using a highly responsive GraphQL API.

## 1. Setup Instructions
Ensure you have Python **3.9+** and `pip` installed.

1. Create and optionally activate a Python Virtual Environment (`.venv`):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   source .venv/bin/activate # Mac/Linux
   ```
2. Install the necessary depedencies from the `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the test SQLite database using the provided script (adds 100+ items):
   ```bash
   python seed_100.py
   python seed.py
   ```

## 2. How to Run the Application
### Locally (Natively)
Start the Uvicorn webserver with Hot Reloading:
```bash
uvicorn main:app --reload
```
The App will be responsive at `http://localhost:8000/graphql` containing the Strawberry Workspace / GraphQL UI Playground.

### Running With Docker (Optional Enhancement)
You can choose to spin up the application entirely in a Docker Orchestrated container:
```bash
docker-compose up --build
```
This isolates the database volume (`db_data`) and serves the backend on `localhost:8000`.

## 3. How to Run Tests
The system uses `pytest` configured with an In-Memory SQLite configuration pattern to quickly assert logic stability and database validation.
To execute, remain in this root directory and type:
```bash
python -m pytest
# or
pytest -v
```
Tests currently cover **Bulk Import Logic**, Database rollback sequences, **Schema query parameters**, and **Stock Status computation**.

## 4. Architecture Overview
- **Core Framework:** **FastAPI**. Built for extreme performance, automated OpenAPI mapping (if needed), and deeply integrated async I/O typing.
- **Language / Typings:** **Python 3**. Leverages Pydantic paradigms naturally built-in with FastAPI routers.
- **GraphQL Engine:** **Strawberry GraphQL**. Chosen over older Python Graphene architectures due to its robust native support for Python `dataclasses` and type hints.
- **ORM / Database Layer:** **SQLAlchemy**. Connects to a local SQLite structure for simple deployment, avoiding heavy configurations. It handles offset/limit paginations and transactions safely locally during Bulk Imports.
- **Multipart Uploads:** Utilizing `python-multipart` bridged specifically to the Strawberry `Upload` scalar context.

## 5. Assumptions Made
- **Stock Status Computation:**
  - `Out of Stock`: `quantity_on_hand` <= 0
  - `Low Stock`: `quantity_on_hand` > 0 AND `quantity_on_hand` <= `reorder_threshold`
  - `In Stock`: `quantity_on_hand` > `reorder_threshold`
- **Partial Success Strategy (Bulk Import):**
  If a company uploads thousands of lines of an Inventory CSV and line 951 contains a syntax error, it is assumed the company would prefer 999 records processed and a single error logged, rather than rolling back the entire payload. I programmed a loop `try...except` combining `db.flush()` and a final `db.commit()` that aggregates `{ validationErrors[] }` directly per failing row.
- **Adjustment Logic:** Assumed that a transaction row set to `adjustment` hard-resets the quantity count exactly to the new number rather than adding/subtracting it.

## 6. Tradeoffs or Limitations
- **File Parsing In Memory:** The CSV bulk import presently halts the HTTP main thread to read and apply lines sequentially. A heavy 5GB file will strangle the UI thread timeout due to the sync operation design logic currently implemented inside the GraphQL Mutation.
- **Database Architecture:** Used a file-based SQLite database to ensure the ease of evaluation logic and speed of setup. SQLite struggles with high concurrent writing connections during massive transactional bulks compared to PostgreSQL databases.
- **No Access Control:** System functions without Authorization Headers (JWT) to ease the current integration pipeline, thereby lacking Audit History Tracking for "Who" actually uploaded a CSV.

## 7. Improvements With More Time
- **Background Task Brokers (Celery/Redis):** Push the Bulk File processing into a background worker queue, parse it there asynchronously, and return an "ImportJobID" initially to the frontend so it can poll its success visually.
- **PostgreSQL Migration:** Move off SQLite and scale the connection configurations with `SQLAlchemy` pooled configurations.
- **Global Error Monitoring:** Implement tools like `Sentry` to log fatal validation errors or network failures globally via unified middleware.
- **API Analytics Documentation:** Expand tests with broader coverage algorithms using factories and generate `coverage HTML` tracking limits.
