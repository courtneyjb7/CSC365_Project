from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_character():
    assert True == True