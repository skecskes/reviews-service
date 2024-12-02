import pytest
from unittest.mock import MagicMock, patch

import polars as pl
from polars import Schema, DataFrame, Int64, String, Date

from src.common.ingestor_interface import IngestorInterface
from src.common.db import SessionLocal
from src.common.csv_reviews_ingestor import CsvReviews


class TestCsvReviewsIngestor:


    def test_can_initialize_csv_reviews(self):
        # Arrange
        db_session = MagicMock(spec=SessionLocal)

        # Act
        csv_reviews_ingestor = CsvReviews("path/to/file.csv", db_session)

        # Assert
        assert csv_reviews_ingestor._seed is not None
        assert csv_reviews_ingestor._db is db_session
        assert csv_reviews_ingestor._file_path == "path/to/file.csv"

    def test_csv_reviews_implements_ingestor_interface(self):
        # Arrange
        db_session = MagicMock(spec=SessionLocal)

        # Act
        csv_reviews_ingestor = CsvReviews("path/to/file.csv", db_session)

        # Assert
        assert issubclass(CsvReviews, IngestorInterface)
        assert hasattr(csv_reviews_ingestor, "ingest")
        assert callable(getattr(csv_reviews_ingestor, "ingest"))
        assert hasattr(csv_reviews_ingestor, "_read_data")
        assert callable(getattr(csv_reviews_ingestor, "_read_data"))
        assert hasattr(csv_reviews_ingestor, "_transform_data")
        assert callable(getattr(csv_reviews_ingestor, "_transform_data"))
        assert hasattr(csv_reviews_ingestor, "_write_data")
        assert callable(getattr(csv_reviews_ingestor, "_write_data"))

    def test_read_data(self):
        # Arrange
        db_session = MagicMock(spec=SessionLocal)
        csv_file = "tests/unit/test_reviews.csv"
        csv_reviews_ingestor = CsvReviews(csv_file, db_session)

        # Act
        df = csv_reviews_ingestor._read_data()

        # Assert
        assert isinstance(df, DataFrame)
        assert df.shape == (2, 7)
        assert df.schema == Schema(
            {
                'Reviewer Name': String,
                'Review Title': String,
                'Review Rating': Int64,
                'Review Content': String,
                'Email Address': String,
                'Country': String,
                'Review Date': String
            }
        )

    def test_transform_data(self):
        # Arrange
        db_session = MagicMock(spec=SessionLocal)
        csv_file = "tests/unit/test_reviews.csv"
        csv_reviews_ingestor = CsvReviews(csv_file, db_session)
        df = csv_reviews_ingestor._read_data()

        # Act
        transformed_df = csv_reviews_ingestor._transform_data(df)

        # Assert
        assert transformed_df is not None
        assert transformed_df.shape == (1, 7)
        assert transformed_df.schema == Schema(
            {
                'reviewer_name': String,
                'review_title': String,
                'review_rating': Int64,
                'review_content': String,
                'email_address': String,
                'country': String,
                'review_date': Date
            }
        )

    @patch('src.common.csv_reviews_ingestor.SessionLocal')
    def test_write_data_with_df(self, db_session):
        # Arrange
        csv_reviews_ingestor = CsvReviews("tests/unit/test_reviews.csv", db_session)
        df = MagicMock(spec=DataFrame)
        df.is_empty.return_value = False

        # Act
        csv_reviews_ingestor._write_data(df)

        # Assert
        # asser not called
        df.write_database.assert_called_once()
        db_session.mock_calls[1][0] == "__enter__().commit"

    @patch('src.common.csv_reviews_ingestor.SessionLocal')
    def test_write_data_empty_df(self, db_session):
        # Arrange
        csv_reviews_ingestor = CsvReviews("tests/unit/test_reviews.csv", db_session)
        df = MagicMock(spec=DataFrame)
        df.is_empty.return_value = True

        # Act
        csv_reviews_ingestor._write_data(df)

        # Assert
        df.write_database.assert_not_called()
        db_session.commit.assert_not_called()

    @pytest.mark.parametrize("email", [
        ("invalid_email", False),
        ("mr.kecske@gmail.com", True),
        ("a@b.c", True),
        ("invalid@email", False)
    ])
    def test_is_invalid_email(self, email):
        # Act
        is_valid = CsvReviews.is_valid_email(email[0])

        # Assert
        assert is_valid is email[1]

    @pytest.mark.parametrize("rating", [
        (-1, False),
        (0, False),
        (1, True),
        (2, True),
        (3, True),
        (4, True),
        (5, True),
        (6, False)
    ])
    def test_is_invalid_rating(self, rating):
        # Act
        is_valid = CsvReviews.is_valid_rating(rating[0])

        # Assert
        assert is_valid is rating[1]