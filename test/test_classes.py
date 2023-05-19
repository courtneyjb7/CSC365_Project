from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_add_classes_invalid_class_type(capsys):
    response = client.post("/classes/0", 
                            json=
                            {
                                "month": 5,
                                "day": 26,
                                "year": 2020,
                                "start_hour": 12,
                                "start_minutes": 30,
                                "end_hour": 1,
                                "end_minutes": 30,
                                "class_type_id": 5
                            })
    assert response.status_code == 200

    captured = capsys.readouterr()
    assert captured.out.strip() == "Error returned: <<<foreign key violation>>>"

def test_add_classes():
    response = client.post("/classes/0", 
                            json=
                            {
                                "month": 5,
                                "day": 26,
                                "year": 2020,
                                "start_hour": 12,
                                "start_minutes": 30,
                                "end_hour": 1,
                                "end_minutes": 30,
                                "class_type_id": 0
                            })
    assert response.status_code == 200


# TODO: how to test put method

def test_add_attendance_existing():
    response = client.put("/classes/7/0/attendance", 
                            json=
                            {
                                "month": 12,
                                "day": 10,
                                "year": 2022,
                                "hour": 11,
                                "minutes": 1
                            })
    assert response.status_code == 200


def test_add_attendance_new():
    response = client.put("/classes/4/1/attendance", 
                            json=
                            {
                                "month": 10,
                                "day": 20,
                                "year": 2022,
                                "hour": 10,
                                "minutes": 0
                            })
    assert response.status_code == 200



def test_get_clas_404():
    response = client.get("/classes/-1")
    assert response.status_code == 404


def test_get_class_1():
    response = client.get("/classes/1")
    assert response.status_code == 200

    with open("test/classes/1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_class_2():
    response = client.get("/classes/8")
    assert response.status_code == 200

    with open("test/classes/8.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_classes_limit():
    response = client.get("/classes/?limit=7&offset=0")
    assert response.status_code == 200

    with open("test/classes/limit=7&offset=0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_classes_filter():
    response = client.get("/classes/?type=begin&limit=2&offset=0")
    assert response.status_code == 200

    with open("test/classes/type=begin&limit=2&offset=0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_post_and_delete_class_1():
    response = client.post("/classes/0", 
                            json=
                            {
                                "month": 5,
                                "day": 26,
                                "year": 2020,
                                "start_hour": 12,
                                "start_minutes": 30,
                                "end_hour": 1,
                                "end_minutes": 30,
                                "class_type_id": 0
                            })
    assert response.status_code == 200

    del_response = client.get(f"/classes/{response.text}")
    assert del_response.status_code == 200

def test_post_and_delete_class_2():
    response = client.post("/classes/1", 
                            json=
                            {
                                "month": 3,
                                "day": 10,
                                "year": 2021,
                                "start_hour": 10,
                                "start_minutes": 0,
                                "end_hour": 12,
                                "end_minutes": 30,
                                "class_type_id": 2
                            })
    assert response.status_code == 200

    del_response = client.get(f"/classes/{response.text}")
    assert del_response.status_code == 200

