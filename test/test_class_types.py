from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_class_types():
    response = client.get("/class-types")
    assert response.status_code == 200

    with open("test/class_types/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

# TODO: need second test case