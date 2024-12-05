from enum import StrEnum

from src.application.list_entity import ListEntity
from src.application.listing import ListInput
from src.domain.category import Category


class CategorySortableFields(StrEnum):
    NAME = "name"
    DESCRIPTION = "description"


class ListCategoryInput(ListInput):
    sort: CategorySortableFields | None = CategorySortableFields.NAME


class ListCategory(ListEntity[Category]):
    pass
