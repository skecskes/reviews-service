from src.common.db import ensure_db_ready, get_db_connection
from src.common.csv_reviews_ingestor import CsvReviews

RAW_DATA_PATH = "src/raw_layer/dataops_tp_reviews.csv"


if __name__ == "__main__":
    ensure_db_ready()
    csv = CsvReviews(RAW_DATA_PATH, get_db_connection())
    csv.ingest()