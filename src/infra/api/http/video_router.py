from typing import Any

from fastapi import Depends, Query, APIRouter

from src.application.list_video import VideoSortableFields, ListVideo, ListVideoInput
from src.application.listing import ListOutput
from src.domain.video import Video
from src.domain.video_repository import VideoRepository
from src.infra.api.http.dependencies import common_parameters, get_video_repository

router = APIRouter()


@router.get("/", response_model=ListOutput[Video])
def list_videos(
    repository: VideoRepository = Depends(get_video_repository),
    sort: VideoSortableFields = Query(VideoSortableFields.TITLE, description="Field to sort by"),
    common: dict[str, Any] = Depends(common_parameters),
) -> ListOutput[Video]:
    return ListVideo(repository=repository).execute(
        ListVideoInput(
            **common,
            sort=sort,
        )
    )
