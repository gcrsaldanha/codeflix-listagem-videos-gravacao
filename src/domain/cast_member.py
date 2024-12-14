from enum import StrEnum

from src.domain.entity import Entity


class CastMemberType(StrEnum):
    ACTOR = "ACTOR"
    DIRECTOR = "DIRECTOR"


class CastMember(Entity):
    name: str
    type: CastMemberType
