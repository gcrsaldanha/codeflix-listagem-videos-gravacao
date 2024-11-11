import logging
from datetime import datetime
from unittest.mock import create_autospec
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.category import Category
from src.elasticsearch_category_repository import (
    ElasticsearchCategoryRepository,
    CATEGORY_INDEX,
    ELASTICSEARCH_HOST_TEST,
)


class TestSearch:
    @pytest.fixture
    def movie_category(self) -> Category:
        return Category(
            id=uuid4(),
            name="Filme",
            description="Categoria de filmes",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

    @pytest.fixture
    def series_category(self) -> Category:
        return Category(
            id=uuid4(),
            name="Séries",
            description="Categoria de séries",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

    @pytest.fixture
    def es(self) -> Elasticsearch:
        client = Elasticsearch(hosts=[ELASTICSEARCH_HOST_TEST])
        if not client.indices.exists(index=CATEGORY_INDEX):
            client.indices.create(index=CATEGORY_INDEX)

        yield client
        client.indices.delete(index=CATEGORY_INDEX)

    def test_can_reach_elasticsearch_test_database(self, es: Elasticsearch) -> None:
        assert es.ping()

    def test_when_index_is_empty_then_return_empty_list(
        self,
        es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=es)

        assert repository.search() == []

    def test_when_index_has_categories_then_return_mapped_categories_with_default_search(
        self,
        es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
    ) -> None:
        es.index(
            index=CATEGORY_INDEX,
            id=str(movie_category.id),
            body=movie_category.model_dump(mode='json'),
            refresh=True,
        )
        es.index(
            index=CATEGORY_INDEX,
            id=str(series_category.id),
            body=series_category.model_dump(mode='json'),
            refresh=True,
        )
        repository = ElasticsearchCategoryRepository(client=es)

        categories = repository.search()

        assert categories == [movie_category, series_category]

    def test_when_index_has_malformed_categories_then_return_valid_categories_and_log_error(
        self,
        es: Elasticsearch,
        movie_category: Category,
    ) -> None:
        es.index(
            index=CATEGORY_INDEX,
            id=str(movie_category.id),
            body=movie_category.model_dump(mode='json'),
            refresh=True,
        )
        es.index(
            index=CATEGORY_INDEX,
            id=str(uuid4()),
            body={"name": "Malformed"},
            refresh=True,
        )
        mock_logger = create_autospec(logging.Logger)
        repository = ElasticsearchCategoryRepository(client=es, logger=mock_logger)

        categories = repository.search()

        assert categories == [movie_category]
        mock_logger.error.assert_called_once()
