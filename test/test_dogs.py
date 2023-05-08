from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_get_dogs():
    response = client.get("/dogs/1")
    assert response.status_code == 200

    with open("test/dogs/1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_dogs_400():
    response = client.get("/dogs/-1")
    assert response.status_code == 404