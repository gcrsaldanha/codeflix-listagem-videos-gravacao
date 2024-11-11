import logging
from datetime import datetime
from unittest.mock import create_autospec
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.category import Category
from src.category_repository import SortDirection
from src.elasticsearch_category_repository import (
    ElasticsearchCategoryRepository,
    ELASTICSEARCH_HOST_TEST,
)


@pytest.fixture
def movie_category() -> Category:
    return Category(
        id=uuid4(),
        name="Filme",
        description="Categoria de filmes",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def series_category() -> Category:
    return Category(
        id=uuid4(),
        name="Séries",
        description="Categoria de séries",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def documentary_category() -> Category:
    return Category(
        id=uuid4(),
        name="Documentários",
        description="Categoria de documentários",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def es() -> Elasticsearch:
    client = Elasticsearch(hosts=[ELASTICSEARCH_HOST_TEST])
    if not client.indices.exists(index=ElasticsearchCategoryRepository.INDEX):
        client.indices.create(index=ElasticsearchCategoryRepository.INDEX)

    yield client
    client.indices.delete(index=ElasticsearchCategoryRepository.INDEX)


@pytest.fixture
def populated_es(
    es: Elasticsearch,
    movie_category: Category,
    series_category: Category,
    documentary_category: Category,
) -> Elasticsearch:
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(movie_category.id),
        body=movie_category.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(series_category.id),
        body=series_category.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(documentary_category.id),
        body=documentary_category.model_dump(mode="json"),
        refresh=True,
    )

    return es


class TestSearch:
    def test_can_reach_elasticsearch_test_database(self, es: Elasticsearch) -> None:
        assert es.ping()

    def test_when_index_is_empty_then_return_empty_list(
        self,
        es: Elasticsearch,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=es)

        assert repository.search() == []

    def test_when_index_has_categories_then_return_mapped_categories_with_default_search(
        self,
        populated_es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
        documentary_category: Category,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=populated_es)

        categories = repository.search()

        assert categories == [movie_category, series_category, documentary_category]

    def test_when_index_has_malformed_categories_then_return_valid_categories_and_log_error(
        self,
        es: Elasticsearch,
        movie_category: Category,
    ) -> None:
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(movie_category.id),
            body=movie_category.model_dump(mode="json"),
            refresh=True,
        )
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(uuid4()),
            body={"name": "Malformed"},
            refresh=True,
        )
        mock_logger = create_autospec(logging.Logger)
        repository = ElasticsearchCategoryRepository(client=es, logger=mock_logger)

        categories = repository.search()

        assert categories == [movie_category]
        mock_logger.error.assert_called_once()

    def test_when_search_term_matches_category_name_then_return_matching_entities(
        self,
        populated_es: Elasticsearch,
        movie_category: Category,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=populated_es)

        categories = repository.search(search="Filme")

        assert categories == [movie_category]

    def test_search_term_matches_both_name_and_description(
        self,
        populated_es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
        documentary_category: Category,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=populated_es)

        categories = repository.search(search="Categoria")

        # Todos contêm a palavra "Categoria" no nome ou descrição
        assert categories == [movie_category, series_category, documentary_category]

    def test_search_is_case_insensitive(
        self,
        populated_es: Elasticsearch,
        movie_category: Category,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=populated_es)

        categories = repository.search(search="filme")

        assert categories == [movie_category]

    def test_search_by_non_existent_term_then_return_empty_list(
        self,
        populated_es: Elasticsearch,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=populated_es)

        categories = repository.search(search="Non-existent")

        assert categories == []


class TestOrdering:
    def test_when_no_sorting_is_specified_then_return_categories_ordered_by_insertion_order(
        self,
        es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
        documentary_category: Category,
    ) -> None:
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            body=series_category.model_dump(mode="json"),
            refresh=True,
        )
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(movie_category.id),
            body=movie_category.model_dump(mode="json"),
            refresh=True,
        )
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(documentary_category.id),
            body=documentary_category.model_dump(mode="json"),
            refresh=True,
        )
        repository = ElasticsearchCategoryRepository(client=es)

        categories = repository.search()

        assert categories == [series_category, movie_category, documentary_category]

    def test_return_categories_ordered_by_name_asc(
        self,
        es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
        documentary_category: Category,
    ) -> None:
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(movie_category.id),
            body=movie_category.model_dump(mode="json"),
            refresh=True,
        )
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(series_category.id),
            body=series_category.model_dump(mode="json"),
            refresh=True,
        )
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(documentary_category.id),
            body=documentary_category.model_dump(mode="json"),
            refresh=True,
        )
        repository = ElasticsearchCategoryRepository(client=es)

        categories = repository.search(sort="name", direction=SortDirection.ASC)

        assert categories == [documentary_category, movie_category, series_category]

    def test_return_categories_ordered_by_name_desc(
        self,
        es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
        documentary_category: Category,
    ) -> None:
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(movie_category.id),
            body=movie_category.model_dump(mode="json"),
            refresh=True,
        )
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(series_category.id),
            body=series_category.model_dump(mode="json"),
            refresh=True,
        )
        es.index(
            index=ElasticsearchCategoryRepository.INDEX,
            id=str(documentary_category.id),
            body=documentary_category.model_dump(mode="json"),
            refresh=True,
        )
        repository = ElasticsearchCategoryRepository(client=es)

        categories = repository.search(sort="name", direction=SortDirection.DESC)

        assert categories == [series_category, movie_category, documentary_category]


class TestPagination:
    def test_when_no_page_is_requested_then_return_default_paginated_response(
        self,
        populated_es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
        documentary_category: Category,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=populated_es)

        categories = repository.search(sort="name")

        assert categories == [documentary_category, movie_category, series_category]

    def test_when_page_is_requested_then_return_expected_paginated_response(
        self,
        populated_es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
        documentary_category: Category,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=populated_es)

        # Page 1
        categories = repository.search(sort="name", page=1, per_page=2)
        assert categories == [documentary_category, movie_category]

        # Page 2
        categories = repository.search(sort="name", page=2, per_page=2)
        assert categories == [series_category]

    def test_when_requested_page_is_out_of_bounds_then_return_empty_list(
        self,
        populated_es: Elasticsearch,
    ) -> None:
        repository = ElasticsearchCategoryRepository(client=populated_es)

        categories = repository.search(sort="name", page=100, per_page=5)

        assert categories == []
