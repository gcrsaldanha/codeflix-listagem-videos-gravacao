from typing import Any

from fastapi import Depends, Query, APIRouter

from src.application.list_genre import GenreSortableFields, ListGenre, ListGenreInput
from src.application.listing import ListOutput
from src.domain.genre import Genre
from src.domain.genre_repository import GenreRepository
from src.infra.api.http.dependencies import common_parameters, get_genre_repository

router = APIRouter()


@router.get("/", response_model=ListOutput[Genre])
def list_genres(
    repository: GenreRepository = Depends(get_genre_repository),
    sort: GenreSortableFields = Query(GenreSortableFields.NAME, description="Field to sort by"),
    common: dict[str, Any] = Depends(common_parameters),
) -> ListOutput[Genre]:
    return ListGenre(repository=repository).execute(
        ListGenreInput(
            search=common["search"],
            page=common["page"],
            per_page=common["per_page"],
            sort=sort,
            direction=common["direction"],
        )
    )
