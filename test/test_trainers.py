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


def test_add_trainer_1():
    trainer = {
        "first_name": "Bob",
        "last_name": "Doe",
        "email": "BobDoe@gmail.com",
        "password": "password5"
    }

    response = client.post(
        "/trainers/",
        json=trainer
    ) 
    
    assert response.status_code == 200



def test_add_trainer_2():
    trainer = {
        "first_name": "Bob",
        "last_name": "Doe",
        "email": "BobDoe@gmail.com",
        "password": "password5"
    }

    response = client.post(
        "/trainers/",
        json=trainer
    ) 
    
    assert response.status_code == 404


def test_verify_password_1():
    response = client.get("/trainers/JaneDoe%40gmail.com/password2")
    assert response.status_code == 200

    with open("test/trainers/verify-jane.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_verify_password_2():
    response = client.get("/trainers/JohnD%40gmail.com/password")
    assert response.status_code == 404