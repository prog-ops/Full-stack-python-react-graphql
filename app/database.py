from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Using SQLite for easy local test
# For usage with MySQL, just replace this string: "mysql+pymysql://user:pass@localhost/dbname"
SQLALCHEMY_DATABASE_URL = "sqlite:///./inventory.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize table (called when the app starts)
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency generator to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()