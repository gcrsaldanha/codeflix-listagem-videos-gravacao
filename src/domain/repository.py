from abc import ABC, abstractmethod
from enum import StrEnum

from src.application.listing import SortDirection, DEFAULT_PAGINATION_SIZE
from src.domain.entity import Entity


class Repository[T: Entity](ABC):
    @abstractmethod
    def search(
        self,
        page: int = 1,
        per_page: int = DEFAULT_PAGINATION_SIZE,
        search: str | None = None,
        sort: StrEnum | None = None,
        direction: SortDirection = SortDirection.ASC,
    ) -> list[T]:
        raise NotImplementedError
