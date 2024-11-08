from enum import StrEnum

from pydantic import BaseModel
from pydantic.fields import Field

from src.category import Category
from src.category_repository import (
    CategoryRepository,
    DEFAULT_PAGINATION_SIZE,
    SortDirection,
)


class SortableFields(StrEnum):
    NAME = "name"
    DESCRIPTION = "description"


class ListCategoryOutputMeta(BaseModel):
    page: int = 1
    per_page: int = DEFAULT_PAGINATION_SIZE
    sort: str | None = None
    direction: SortDirection = SortDirection.ASC


class ListCategoryOutput(BaseModel):
    data: list[Category] = Field(default_factory=list)
    meta: ListCategoryOutputMeta = Field(default_factory=ListCategoryOutputMeta)


class ListCategoryInput(BaseModel):
    search: str | None = None
    page: int = 1
    per_page: int = DEFAULT_PAGINATION_SIZE
    sort: SortableFields = SortableFields.NAME
    direction: SortDirection = SortDirection.ASC


class ListCategory:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    def execute(self, input: ListCategoryInput) -> ListCategoryOutput:
        categories: list[Category] = self.repository.search(
            page=input.page,
            per_page=input.per_page,
            search=input.search,
            sort=input.sort,
            direction=input.direction,
        )

        return ListCategoryOutput(
            data=categories,
            meta=ListCategoryOutputMeta(
                page=input.page,
                per_page=input.per_page,
                sort=input.sort,
                direction=input.direction,
            ),
        )
