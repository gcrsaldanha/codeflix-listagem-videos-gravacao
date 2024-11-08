from abc import ABC, abstractmethod
from enum import StrEnum

from src.category import Category


DEFAULT_PAGINATION_SIZE = 5


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class CategoryRepository(ABC):
    @abstractmethod
    def search(
        self,
        page: int = 1,
        per_page: int = DEFAULT_PAGINATION_SIZE,
        search: str | None = None,
        sort: str | None = None,
        direction: SortDirection = SortDirection.ASC,
    ) -> list[Category]:
        raise NotImplementedError
