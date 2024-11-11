from datetime import datetime
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.domain.category import Category
from src.infra.elasticsearch.elasticsearch_category_repository import (
    ElasticsearchCategoryRepository,
    ELASTICSEARCH_HOST_TEST,
)
from src.application.list_category import (
    ListCategory,
    ListCategoryInput,
    ListCategoryOutputMeta,
    SortableFields,
    SortDirection,
)


@pytest.fixture
def movie() -> Category:
    return Category(
        id=uuid4(),
        name="Filme",
        description="Categoria de filmes",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def series() -> Category:
    return Category(
        id=uuid4(),
        name="Séries",
        description="Categoria de séries",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def documentary() -> Category:
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
    movie: Category,
    series: Category,
    documentary: Category,
) -> Elasticsearch:
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(movie.id),
        body=movie.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(series.id),
        body=series.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(documentary.id),
        body=documentary.model_dump(mode="json"),
        refresh=True,
    )

    return es


class TestListCategory:
    def test_list_categories_with_default_values(
        self,
        populated_es: Elasticsearch,
        movie: Category,
        series: Category,
        documentary: Category,
    ) -> None:
        list_category = ListCategory(
            repository=ElasticsearchCategoryRepository(client=populated_es)
        )
        output = list_category.execute(input=ListCategoryInput())

        assert output.data == [documentary, movie, series]  # Ordered by name by default
        assert output.meta == ListCategoryOutputMeta(
            page=1,
            per_page=5,
            sort=SortableFields.NAME,
            direction=SortDirection.ASC,
        )

    def test_list_categories_with_pagination_sorting_and_search(
        self,
        populated_es: Elasticsearch,
        movie: Category,
        series: Category,
        documentary: Category,
    ) -> None:
        list_category = ListCategory(
            repository=ElasticsearchCategoryRepository(client=populated_es)
        )

        # Page 1
        output = list_category.execute(
            input=ListCategoryInput(
                search="Filme",
                sort=SortableFields.NAME,
                direction=SortDirection.DESC,
                page=1,
                per_page=1,
            )
        )

        assert output.data == [movie]
        assert output.meta == ListCategoryOutputMeta(
            page=1,
            per_page=1,
            sort=SortableFields.NAME,
            direction=SortDirection.DESC,
        )

        # Page 2
        output = list_category.execute(
            input=ListCategoryInput(
                search="Filme",
                sort=SortableFields.NAME,
                direction=SortDirection.DESC,
                page=2,
                per_page=1,
            )
        )

        assert output.data == []
        assert output.meta == ListCategoryOutputMeta(
            page=2,
            per_page=1,
            sort=SortableFields.NAME,
            direction=SortDirection.DESC,
        )
