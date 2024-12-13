from enum import StrEnum

from src.application.list_entity import ListEntity
from src.application.listing import ListInput
from src.domain.video import Video


class VideoSortableFields(StrEnum):
    TITLE = "title"


class ListVideoInput(ListInput):
    sort: VideoSortableFields | None = VideoSortableFields.TITLE


class ListVideo(ListEntity[Video]):
    pass
