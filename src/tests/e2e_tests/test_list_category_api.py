from fastapi.testclient import TestClient

from src.infra.api.http.main import app


def test_list_categories_empty_response():
    client = TestClient(app=app)
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == {
        "data": [],
        "meta": {
            "page": 1,
            "per_page": 5,
            "sort": "name",
            "direction": "asc",
        }
    }
