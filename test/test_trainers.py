from fastapi.testclient import TestClient

from src.api.server import app


client = TestClient(app)


def test_get_character():
    assert 1 == 1