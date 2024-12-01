from abc import ABC, abstractmethod

from polars import DataFrame


class IngestorInterface(ABC):

    @abstractmethod
    def ingest(self):
        pass

    @abstractmethod
    def _read_data(self) -> DataFrame:
        pass

    @abstractmethod
    def _transform_data(self, df: DataFrame) -> DataFrame:
        pass

    @abstractmethod
    def _write_data(self, df: DataFrame):
        pass