from enum import StrEnum
from uuid import UUID

from pydantic import HttpUrl

from src.domain.entity import Entity


class Rating(StrEnum):
    ER = "ER"
    L = "L"
    AGE_10 = "AGE_10"
    AGE_12 = "AGE_12"
    AGE_14 = "AGE_14"
    AGE_16 = "AGE_16"
    AGE_18 = "AGE_18"


class Video(Entity):
    title: str
    launch_year: int
    rating: Rating
    categories: set[UUID]
    genres: set[UUID]
    cast_members: set[UUID]
    banner_url: HttpUrl
    # TODO: other relevant attributes if we want to
    # Also, categories, genres, cast_members could be nested objects instead of UUIDs
