from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_get_dogs():
    response = client.get("/dogs/")
    assert response.status_code == 200

    with open("test/dogs/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_dogs_2():
    response = client.get("/dogs/?limit=1&offset=1")
    assert response.status_code == 200

    with open("test/dogs/limit=1&offset=1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_dog_1():
    response = client.get("/dogs/1")
    assert response.status_code == 200

    with open("test/dogs/1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_dog_2():
    response = client.get("/dogs/2")
    assert response.status_code == 200

    with open("test/dogs/2.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_post_comment_1():
    comment = {
        "trainer_id": 1,
        "comment_text": "More improvement"
    }

    response = client.post(
        "/dogs/0/comments/",
        json=comment
    ) 
    
    assert response.status_code == 200

def test_error_post_comment():
    comment = {
        "trainer_id": 500,
        "comment_text": "More improvement"
    }

    response = client.post(
        "/dogs/0/comments/",
        json=comment
    ) 

    assert response.status_code == 404
    
def test_get_dog_404():
    response = client.get("/dogs/-1")
    assert response.status_code == 404

def test_delete_comment_1():
    response = client.delete(
        "/dogs/dogs/comments/7"
    ) 
    
    assert response.status_code == 200


def test_delete_comment_2():
    response = client.delete(
        "/dogs/dogs/comments/500"
    ) 
    
    assert response.status_code == 404