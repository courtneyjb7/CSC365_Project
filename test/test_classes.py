from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_add_classes_invalid_class_type(capsys):
    response = client.post("/classes/", 
                            json=
                            {
                                "trainer_id": 500,
                                "month": 12,
                                "day": 1,
                                "year": 2024,
                                "start_hour": 10,
                                "start_minutes": 0,
                                "end_hour": 10,
                                "end_minutes": 0,
                                "class_type_id": 0,
                                "room_id": 0
                            })
    assert response.status_code == 404

    with open("test/classes/trainer=500.json", 
              encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_add_classes():
    response = client.post("/classes/", 
                            json=
                            {
                                "trainer_id": 0,
                                "month": 12,
                                "day": 1,
                                "year": 2020,
                                "start_hour": 10,
                                "start_minutes": 0,
                                "end_hour": 10,
                                "end_minutes": 0,
                                "class_type_id": 0,
                                "room_id": 0
                            })
    assert response.status_code == 200

    assert response.json() == "success"

def test_add_classes_unavail_room():
    response = client.post("/classes/", 
                            json=
                            {
                                "trainer_id": 0,
                                "month": 1,
                                "day": 1,
                                "year": 2023,
                                "start_hour": 13,
                                "start_minutes": 0,
                                "end_hour": 14,
                                "end_minutes": 0,
                                "class_type_id": 0,
                                "room_id": 1
                            })
    assert response.status_code == 404

    assert response.json() == {
        "detail": "the provided room is unavailable at this day/time."
    }

def test_add_attendance_existing():
    response = client.post("/classes/1/attendance?dog_id=1")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "dog already checked into this class."
    }


def test_add_attendance_new():
    response = client.post("/classes/4/attendance?dog_id=2")
    assert response.status_code == 200
    assert response.json() == "success"


def test_get_class_404():
    response = client.get("/classes/-1")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "class not found."
    }


def test_get_class_1():
    response = client.get("/classes/1")
    assert response.status_code == 200

    with open("test/classes/1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_classes_limit():
    response = client.get("/classes/?limit=5&offset=0")
    assert response.status_code == 200

    with open("test/classes/limit=5.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_classes_offset():
    response = client.get("/classes/?limit=5&offset=2")
    assert response.status_code == 200

    with open("test/classes/limit=5&offset=2.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_delete_class_1():
    del_response = client.get("/classes/500")
    assert del_response.status_code == 404

def test_delete_class_2():
    del_response = client.get("/classes/-1")
    assert del_response.status_code == 404

def test_find_class_no_match():
    response = client.get("/classes/available/?class_type_id\
=1&time_range=midday&day1=Sunday&limit=50")
    assert response.status_code == 200
    assert response.json() == "There are no classes that match this criteria."

def test_find_class():
    response = client.get("classes/available/?class_type_id=0&\
time_range=midday&day1=Sunday&day2=Monday&day3=Thursday&limit=50")
    assert response.status_code == 200

    with open("test/classes/find_class.json", 
              encoding="utf-8") as f:
        assert response.json() == json.load(f)

