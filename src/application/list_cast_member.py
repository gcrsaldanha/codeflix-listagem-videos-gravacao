from enum import StrEnum

from src.application.list_entity import ListEntity
from src.application.listing import ListInput
from src.domain.cast_member import CastMember


class CastMemberSortableFields(StrEnum):
    NAME = "name"


class ListCastMemberInput(ListInput):
    sort: CastMemberSortableFields | None = CastMemberSortableFields.NAME


class ListCastMember(ListEntity[CastMember]):
    pass
