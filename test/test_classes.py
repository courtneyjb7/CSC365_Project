from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)

def add_classes_invalid_class_type(capsys):
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


def add_attendance_existing():
    response = client.post("/classes/7/0/attendance", 
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

    assert response.text == '"Attendance updated"'


def add_attendance_new():
    response = client.post("/classes/4/1/attendance", 
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

    assert response.text == '"Attendance updated"'