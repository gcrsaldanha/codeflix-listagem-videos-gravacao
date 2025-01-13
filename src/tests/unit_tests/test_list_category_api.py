from typing import Iterator
from unittest.mock import create_autospec

import pytest
from fastapi.testclient import TestClient

from src.domain.category_repository import CategoryRepository
from src.infra.api.http.auth import authenticate
from src.infra.api.http.main import app
from src.infra.api.http.dependencies import get_category_repository


@pytest.fixture
def client() -> Iterator[TestClient]:
    mock_category_repository = create_autospec(CategoryRepository)
    app.dependency_overrides[get_category_repository] = lambda: mock_category_repository
    app.dependency_overrides[authenticate] = lambda: None
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_categories_endpoint_with_default_pagination(client):
    response = client.get("/categories")
    assert response.status_code == 200


def test_categories_endpoint_with_custom_pagination(client):
    response = client.get("/categories", params={"page": 2, "per_page": 10})
    assert response.status_code == 200


def test_categories_endpoint_with_search(client):
    response = client.get("/categories", params={"search": "electronics"})
    assert response.status_code == 200


def test_categories_endpoint_with_sorting_asc(client):
    response = client.get("/categories", params={"sort": "name", "direction": "asc"})
    assert response.status_code == 200


def test_categories_endpoint_invalid_sort_field(client):
    response = client.get("/categories", params={"sort": "invalid_field"})
    assert response.status_code == 422
