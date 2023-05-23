from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_get_room_1():
    response = client.get("/rooms/?month=1&day=1&year=2023&\
start_hour=10&start_minutes=0&end_hour=11&end_minutes=0&class_type_id=3")
    assert response.status_code == 200

    with open("test/rooms/month=1&day=1&year=2023&start_hour\
=10&start_minutes=0&end_hour=11&end_minutes=0&class_type_id=3.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_room_unavailable():
    response = client.get("rooms/?month=12&day=1&year=2023&\
start_hour=9&start_minutes=0&end_hour=14&end_minutes=0&class_type_id=4")
    assert response.status_code == 404

    with open("test/rooms/month=12&day=1&year=2023&start_hour\
=9&start_minutes=0&end_hour=14&end_minutes=0&class_type_id=4.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_room_bad_input():
    response = client.get("rooms/?month=0&day=1&year=2024&\
start_hour=10&start_minutes=0&end_hour=11&end_minutes=0&class_type_id=2")
    assert response.status_code == 404

    with open("test/rooms/month=0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)