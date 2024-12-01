import re
import uuid
import datetime

import polars as pl
from polars.dataframe import DataFrame
from sqlalchemy.exc import SQLAlchemyError

from src.common.db import SessionLocal
from src.common.ingestor_interface import IngestorInterface
from src.common.tables import Review, IngestionStatus, IngestionStatusEnum
from src.common.logger import logger


class CsvReviews(IngestorInterface):

    def __init__(self, file_path: str, db_session: SessionLocal):
        self._seed = str(uuid.uuid4())
        self._file_path = file_path
        self._db = db_session

    def ingest(self):
        """Ingest CSV reviews file into the database"""
        try:
            if self._db.query(IngestionStatus).filter(IngestionStatus.seed == self._seed).first():
                logger.info("This ingestion is already in progress", seed=self._seed)
                return
            if self._db.query(IngestionStatus).filter(IngestionStatus.ingestor == self.__class__.__name__, IngestionStatus.status == IngestionStatusEnum.InProcess).first():
                logger.info("Wait while previous ingestion finishes", seed=self._seed)
                return

            self._db.add(IngestionStatus(status=IngestionStatusEnum.InProcess, start_date=datetime.datetime.now(),
                                         ingestor=self.__class__.__name__, seed=self._seed))
            self._db.commit()

            df = self._read_data()
            df = self._transform_data(df)
            self._write_data(df)

            logger.info("Ingestion completed successfully", seed=self._seed)
            ingestion_status = self._db.query(IngestionStatus).filter(IngestionStatus.seed == self._seed).first()
            ingestion_status.status = IngestionStatusEnum.Done
            ingestion_status.end_date = datetime.datetime.now()
            self._db.commit()

        except Exception as e:
            logger.error("Ingestion failed", error=str(e), seed=self._seed)
            ingestion_status = self._db.query(IngestionStatus).filter(IngestionStatus.seed == self._seed).first()
            ingestion_status.status = IngestionStatusEnum.Error
            ingestion_status.end_date = datetime.datetime.now()
            self._db.commit()
            raise e

    def _read_data(self) -> DataFrame:
        """Read CSV file into a DataFrame"""
        try:
            df = pl.read_csv(self._file_path)
            date = datetime.datetime.now().isoformat()
            logger.info("Ingesting reviews file", num_rows=len(df), num_columns=len(df.columns), date=date,
                        schema=df.schema, seed=self._seed)
            return df
        except Exception as e:
            logger.error("Error reading CSV file", error=str(e), seed=self._seed)
            raise e

    def _transform_data(self, df: DataFrame) -> DataFrame:
        """Place for all the transformations"""
        try:
            # align column names
            df = df.rename(
                {
                    "Reviewer Name": "reviewer_name",
                    "Review Title": "review_title",
                    "Review Rating": "review_rating",
                    "Review Content": "review_content",
                    "Email Address": "email_address",
                    "Country": "country",
                    "Review Date": "review_date"
                }
            )

            df = df.with_columns([pl.col("review_date").cast(pl.Date)])
            df = df.drop_nulls()
            df = df.filter(pl.col("review_rating").map_elements(CsvReviews.is_valid_rating, return_dtype=pl.Boolean))
            df = df.with_columns(has_valid_email=pl.col("email_address").map_elements(CsvReviews.is_valid_email,
                                                                                      return_dtype=pl.Boolean))
            df = df.filter(pl.col("has_valid_email")).drop("has_valid_email")

            logger.info("Transformed DataFrame", num_rows=len(df), num_columns=len(df.columns),
                        date=datetime.datetime.now().isoformat(), schema=df.schema, seed=self._seed)
            return df
        except Exception as e:
            logger.error("Error transforming DataFrame", error=str(e), seed=self._seed)
            raise e

    def _write_data(self, df: DataFrame):
        """Write DataFrame to the database"""
        try:
            with self._db as db:
                df.write_database(table_name=Review.__tablename__, connection=db, engine="sqlalchemy",
                                  if_table_exists="append")
                db.commit()
                logger.info("Data successfully written to the database", date=datetime.datetime.now().isoformat(),
                            seed=self._seed)
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error writing to the database", error=str(e), seed=self._seed)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address format"""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def is_valid_rating(rating: int) -> bool:
        """Validate rating value"""
        return 1 <= rating <= 5
