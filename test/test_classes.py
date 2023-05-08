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
                                "year": 2024,
                                "start_hour": 12,
                                "start_minutes": 30,
                                "end_hour": 1,
                                "end_minutes": 30,
                                "class_type_id": 5
                            })
    assert response.status_code == 200

    captured = capsys.readouterr()
    assert captured.out.strip() == "Error returned: <<<Invalid class_type_id>>>"

def test_add_classes():
    response = client.post("/classes/0", 
                            json=
                            {
                                "month": 5,
                                "day": 26,
                                "year": 2024,
                                "start_hour": 12,
                                "start_minutes": 30,
                                "end_hour": 1,
                                "end_minutes": 30,
                                "class_type_id": 0
                            })
    assert response.status_code == 200

    assert response.text == '"Class added"'


# TODO: how to test put method

# def test_add_attendance_existing():
#     response = client.put("/classes/7/0/attendance", 
#                             json=
#                             {
#                                 "month": 5,
#                                 "day": 26,
#                                 "year": 2024,
#                                 "start_hour": 12,
#                                 "start_minutes": 30,
#                                 "end_hour": 1,
#                                 "end_minutes": 30,
#                                 "class_type_id": 0
#                             })
#     assert response.status_code == 200

#     assert response.text == '"Attendance updated"'


# def test_add_attendance_new():
#     response = client.put("/classes/4/1/attendance", 
#                             json=
#                             {
#                                 "month": 5,
#                                 "day": 26,
#                                 "year": 2024,
#                                 "start_hour": 12,
#                                 "start_minutes": 30,
#                                 "end_hour": 1,
#                                 "end_minutes": 30,
#                                 "class_type_id": 0
#                             })
#     assert response.status_code == 200

#     assert response.text == '"Attendance updated"'

def test_get_class():
    response = client.get("/classes/2")
    assert response.status_code == 200

    with open("test/classes/2.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_clas_400():
    response = client.get("/classes/-1")
    assert response.status_code == 404