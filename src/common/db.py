import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.common.tables import Base

PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")

_REVIEWS_SQL_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
_POSTGRES_SQL_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/postgres"
engine = create_engine(_REVIEWS_SQL_URL, pool_size=10, max_overflow=20)
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
    pg_engine = create_engine(_POSTGRES_SQL_URL, isolation_level="AUTOCOMMIT")
    with pg_engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{PGDATABASE}'"))
        if not result.scalar():
            conn.execute(text(f"CREATE DATABASE {PGDATABASE}"))

def create_tables():
    """Create all the tables if they don't exist"""
    Base.metadata.create_all(bind=engine)

def ensure_db_ready():
    """Ensure the database and tables are created"""
    create_database()
    create_tables()
