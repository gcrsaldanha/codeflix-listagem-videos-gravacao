from typing import Iterator

import pytest
from elasticsearch import Elasticsearch
from fastapi.testclient import TestClient

from src.domain.category import Category
from src.domain.category_repository import CategoryRepository
from src.infra.api.http.main import app, get_category_repository
from src.infra.elasticsearch.elasticsearch_category_repository import (
    ElasticsearchCategoryRepository,
)


@pytest.fixture
def populated_category_repository(
    populated_es: Elasticsearch,
) -> Iterator[CategoryRepository]:
    yield ElasticsearchCategoryRepository(client=populated_es)


@pytest.fixture
def test_client_with_populated_repo(
    populated_category_repository: CategoryRepository,
) -> Iterator[TestClient]:
    app.dependency_overrides[get_category_repository] = lambda: populated_category_repository
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_categories(
    test_client_with_populated_repo: TestClient,
    series: Category,
    movie: Category,
    documentary: Category,
) -> None:
    response = test_client_with_populated_repo.get("/categories")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "id": str(documentary.id),
                "name": documentary.name,
                "description": documentary.description,
                "created_at": documentary.created_at.isoformat(),
                "updated_at": documentary.updated_at.isoformat(),
                "is_active": documentary.is_active,
            },
            {
                "id": str(movie.id),
                "name": movie.name,
                "description": movie.description,
                "created_at": movie.created_at.isoformat(),
                "updated_at": movie.updated_at.isoformat(),
                "is_active": movie.is_active,
            },
            {
                "id": str(series.id),
                "name": series.name,
                "description": series.description,
                "created_at": series.created_at.isoformat(),
                "updated_at": series.updated_at.isoformat(),
                "is_active": series.is_active,
            },
        ],
        "meta": {
            "page": 1,
            "per_page": 5,
            "sort": "name",
            "direction": "asc",
        },
    }
