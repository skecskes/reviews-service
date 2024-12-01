from src.common.tables import IngestionStatusEnum

class TestTables:

    def test_ingestion_status_enum(self):
        # Act
        actual = IngestionStatusEnum

        # Assert
        assert actual.Error.value == "Error"
        assert actual.Done.value == "Done"
        assert actual.InProcess.value == "InProcess"
