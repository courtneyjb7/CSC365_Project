from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_class_0():
    response = client.get("/classes/0")
    assert response.status_code == 200

    with open("test/classes/0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_class_1():
    response = client.get("/classes/1")
    assert response.status_code == 200

    with open("test/classes/1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_classes_0():
    response = client.get("/classes/")
    assert response.status_code == 200

    with open("test/classes/classes.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_classes_1():
    response = client.get("/classes/?type=begin&limit=2&offset=0")
    assert response.status_code == 200

    with open("test/classes/type=begin&limit=2&offset=0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_delete_class():
    response = client.get("/classes/50")
    assert response.status_code == 404

# def test_put_attendance():
#     data = {
#         "month": 1,
#         "day": 5,
#         "year": 2023,
#         "hour": 9,
#         "minute": 0
        
#     }

#     response = client.post(
#         "/classes/0/0/attendance",
#         json=data
#     ) 
    
#     assert response.status_code == 200