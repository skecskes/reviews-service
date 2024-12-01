from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SqlEnum
from sqlalchemy.orm import declarative_base

from enum import Enum

class IngestionStatusEnum(Enum):
    """Enum for ingestion status"""
    InProcess = "InProcess"
    Done = "Done"
    Error = "Error"

Base = declarative_base()

class Review(Base):
    """DB Model for reviews tables"""
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_name = Column(String, nullable=False)
    review_title = Column(String, nullable=False)
    review_rating = Column(Integer, nullable=False)
    review_content = Column(String, nullable=False)
    email_address = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False)
    review_date = Column(Date, nullable=False)


class IngestionStatus(Base):
    """DB Model for ingestion_status table"""
    __tablename__ = 'ingestion_status'
    seed = Column(String, nullable=False, unique=True, index=True, primary_key=True)
    status = Column(SqlEnum(IngestionStatusEnum), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    ingestor = Column(String, nullable=False)