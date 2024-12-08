from enum import StrEnum

from src.application.list_entity import ListEntity
from src.application.listing import ListInput
from src.domain.cast_member import CastMember
from src.domain.genre import Genre


class GenreSortableFields(StrEnum):
    NAME = "name"


class ListGenreInput(ListInput):
    sort: GenreSortableFields | None = GenreSortableFields.NAME


class ListGenre(ListEntity[Genre]):
    pass
