from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_class_types():
    response = client.get("/class-types/")
    assert response.status_code == 200

    with open("test/class_types/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_class_types_filter():
    response = client.get("/class-types/?type=puppy&limit=2&offset=0")
    assert response.status_code == 200

    with open("test/class_types/type=puppy&limit=2&offset=0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)
