from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.common.tables import Base

DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/trustpilot"
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get a database connection generator for API endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection() -> SessionLocal:
    """Get a database connection for ingestor tasks"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def create_database():
    """Create the database if it doesn't exist"""
    pg_engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres", isolation_level="AUTOCOMMIT")
    with pg_engine.connect() as conn:
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='trustpilot'"))
        if not result.scalar():
            conn.execute(text("CREATE DATABASE IF NOT EXISTS trustpilot"))

def create_tables():
    """Create all the tables if they don't exist"""
    Base.metadata.create_all(bind=engine)

def ensure_db_ready():
    """Ensure the database and tables are created"""
    create_database()
    create_tables()
