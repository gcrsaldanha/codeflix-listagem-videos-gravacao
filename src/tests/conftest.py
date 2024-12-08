from datetime import datetime
from typing import Generator
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.domain.category import Category
from src.domain.genre import Genre
from src.infra.elasticsearch.elasticsearch_category_repository import (
    ELASTICSEARCH_HOST_TEST,
    ElasticsearchCategoryRepository,
)
from src.infra.elasticsearch.elasticsearch_genre_repository import ElasticsearchGenreRepository


@pytest.fixture
def es() -> Generator[Elasticsearch, None, None]:
    client = Elasticsearch(hosts=[ELASTICSEARCH_HOST_TEST])

    if not client.indices.exists(index=ElasticsearchCategoryRepository.INDEX):
        client.indices.create(index=ElasticsearchCategoryRepository.INDEX)
    if not client.indices.exists(index=ElasticsearchGenreRepository.INDEX):
        client.indices.create(index=ElasticsearchGenreRepository.INDEX)

    yield client

    client.indices.delete(index=ElasticsearchCategoryRepository.INDEX)
    client.indices.delete(index=ElasticsearchGenreRepository.INDEX)


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
def drama(movie: Category, documentary: Category) -> Genre:
    return Genre(
        id=uuid4(),
        name="Drama",
        categories={movie.id, documentary.id},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def romance() -> Genre:
    return Genre(
        id=uuid4(),
        name="Romance",
        categories=set(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def populated_es(
    es: Elasticsearch,
    movie: Category,
    series: Category,
    documentary: Category,
    drama: Genre,
    romance: Genre,
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

    # Genre
    es.index(
        index=ElasticsearchGenreRepository.INDEX,
        id=str(drama.id),
        body=drama.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchGenreRepository.INDEX,
        id=str(romance.id),
        body=romance.model_dump(mode="json"),
        refresh=True,
    )

    # Drama categories
    es.index(
        index=ElasticsearchGenreRepository._GENRE_CATEGORIES_INDEX,
        id=str(uuid4()),
        body={
            "genre_id": str(drama.id),
            "category_id": str(movie.id),
        },
        refresh=True,
    )
    es.index(
        index=ElasticsearchGenreRepository._GENRE_CATEGORIES_INDEX,
        id=str(uuid4()),
        body={
            "genre_id": str(drama.id),
            "category_id": str(documentary.id),
        },
        refresh=True,
    )

    return es
