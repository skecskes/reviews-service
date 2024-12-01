import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="class")
def apitest_classfixture(request):
    """Provides `self.client` that is FastApi TestClient instance"""
    client = TestClient(app)
    request.cls.client = client

    yield

    client.close()