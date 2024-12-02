import sys

from src.common.db import ensure_db_ready, get_db_connection
from src.common.csv_reviews_ingestor import CsvReviews

RAW_DATA_PATH = "src/raw_layer/dataops_tp_reviews.csv"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/ingestion/etl.py <path_to_csv>")
        sys.exit(1)

    file_path = sys.argv[1]
    ensure_db_ready()
    csv = CsvReviews(file_path, get_db_connection())
    csv.ingest()