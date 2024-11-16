from src.application.listing import ListInput, ListOutput, ListOutputMeta
from src.domain.entity import Entity
from src.domain.repository import Repository


"""
Nova sintaxe de generics sendo utilizada.

Também poderíamos fazer:

>>> T = TypeVar("T", bound=Entity)
>>> class ListEntity(Generic[T]):
>>>     ...
"""

class ListEntity[T: Entity]:
    def __init__(self, repository: Repository[T]) -> None:
        self.repository = repository

    def execute(self, input: ListInput) -> ListOutput[T]:
        entities = self.repository.search(
            search=input.search,
            page=input.page,
            per_page=input.per_page,
            sort=input.sort,
            direction=input.direction,
        )
        meta = ListOutputMeta(
            page=input.page,
            per_page=input.per_page,
            sort=input.sort,
            direction=input.direction,
        )
        return ListOutput(data=entities, meta=meta)
