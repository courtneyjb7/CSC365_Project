from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_trainer_0():
    response = client.get("/trainers/0")
    assert response.status_code == 200

    with open("test/trainers/0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_trainer_1():
    response = client.get("/trainers/1")
    assert response.status_code == 200

    with open("test/trainers/1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_trainers():
    response = client.get("/trainers/")
    assert response.status_code == 200

    with open("test/trainers/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)
