from enum import StrEnum

from pydantic import BaseModel, Field

from src.domain.entity import Entity

DEFAULT_PAGINATION_SIZE = 5


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ListOutputMeta(BaseModel):
    page: int = 1
    per_page: int = DEFAULT_PAGINATION_SIZE
    sort: str | None = None
    direction: SortDirection = SortDirection.ASC


class ListOutput[T: Entity](BaseModel):
    data: list[T] = Field(default_factory=list)
    meta: ListOutputMeta = Field(default_factory=ListOutputMeta)


class ListInput[SortableFieldsType: StrEnum](BaseModel):
    search: str | None = None
    page: int = 1
    per_page: int = DEFAULT_PAGINATION_SIZE
    sort: SortableFieldsType | None = None
    direction: SortDirection = SortDirection.ASC
