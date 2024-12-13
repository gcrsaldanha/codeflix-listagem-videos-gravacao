from typing import Any

from fastapi import Query

from src.application.listing import DEFAULT_PAGINATION_SIZE, SortDirection
from src.domain.cast_member_repository import CastMemberRepository
from src.domain.category_repository import CategoryRepository
from src.domain.genre_repository import GenreRepository
from src.domain.video_repository import VideoRepository
from src.infra.elasticsearch.elasticsearch_cast_member_repository import ElasticsearchCastMemberRepository
from src.infra.elasticsearch.elasticsearch_category_repository import ElasticsearchCategoryRepository
from src.infra.elasticsearch.elasticsearch_genre_repository import ElasticsearchGenreRepository
from src.infra.elasticsearch.elasticsearch_video_repository import ElasticsearchVideoRepository


def common_parameters(
    search: str | None = Query(None, description="Search term for name or description"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        DEFAULT_PAGINATION_SIZE,
        ge=1,
        le=100,
        description="Number of items per page",
    ),
    direction: SortDirection = Query(
        SortDirection.ASC, description="Sort direction (asc or desc)"
    ),
) -> dict[str, Any]:
    return {
        "search": search,
        "page": page,
        "per_page": per_page,
        "direction": direction,
    }


def get_category_repository() -> CategoryRepository:
    return ElasticsearchCategoryRepository()


def get_cast_member_repository() -> CastMemberRepository:
    return ElasticsearchCastMemberRepository()


def get_genre_repository() -> GenreRepository:
    return ElasticsearchGenreRepository()


def get_video_repository() -> VideoRepository:
    return ElasticsearchVideoRepository()
