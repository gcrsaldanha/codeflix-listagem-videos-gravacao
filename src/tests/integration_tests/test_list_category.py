from datetime import datetime
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.application.list_category import CategorySortableFields, ListCategory, ListCategoryInput
from src.application.listing import ListOutputMeta
from src.domain.category import Category
from src.domain.repository import SortDirection
from src.infra.elasticsearch.elasticsearch_category_repository import (
    ElasticsearchCategoryRepository,
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
        assert output.meta == ListOutputMeta(
            page=1,
            per_page=5,
            sort=CategorySortableFields.NAME,
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
                sort=CategorySortableFields.NAME,
                direction=SortDirection.DESC,
                page=1,
                per_page=1,
            )
        )

        assert output.data == [movie]
        assert output.meta == ListOutputMeta(
            page=1,
            per_page=1,
            sort=CategorySortableFields.NAME,
            direction=SortDirection.DESC,
        )

        # Page 2
        output = list_category.execute(
            input=ListCategoryInput(
                search="Filme",
                sort=CategorySortableFields.NAME,
                direction=SortDirection.DESC,
                page=2,
                per_page=1,
            )
        )

        assert output.data == []
        assert output.meta == ListOutputMeta(
            page=2,
            per_page=1,
            sort=CategorySortableFields.NAME,
            direction=SortDirection.DESC,
        )
