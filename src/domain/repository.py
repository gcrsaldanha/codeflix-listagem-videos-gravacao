from abc import ABC, abstractmethod

from src.application.listing import SortDirection, DEFAULT_PAGINATION_SIZE
from src.domain.entity import Entity


class Repository[T: Entity](ABC):
    @abstractmethod
    def search(
        self,
        page: int = 1,
        per_page: int = DEFAULT_PAGINATION_SIZE,
        search: str | None = None,
        sort: str | None = None,
        direction: SortDirection = SortDirection.ASC,
    ) -> list[T]:
        raise NotImplementedError
