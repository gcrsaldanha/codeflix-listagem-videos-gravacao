import logging
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.domain.video import Rating, Video
from src.domain.video_repository import VideoRepository
from src.infra.codeflix_client.codeflix_client import CodeflixClient

logger = logging.getLogger(__name__)


class SaveVideoInput(BaseModel):
    id: UUID
    title: str
    launch_year: int
    rating: Rating
    created_at: datetime
    updated_at: datetime
    is_active: bool


class SaveVideo:
    def __init__(self, repository: VideoRepository, codeflix_client: CodeflixClient) -> None:
        self._repository = repository
        self._codeflix_client = codeflix_client

    def execute(self, input: SaveVideoInput) -> None:
        logger.info(f"Saving video with id: {input.id}")

        http_data = self._codeflix_client.get_video(id=input.id)
        categories = {UUID(category["id"]) for category in http_data.categories}
        cast_members = {UUID(cast_member["id"]) for cast_member in http_data.cast_members}
        genres = {UUID(genre["id"]) for genre in http_data.genres}
        banner_url = http_data.banner["raw_location"]

        video = Video(
            **input.model_dump(mode="python"),
            categories=categories,
            cast_members=cast_members,
            genres=genres,
            banner_url=banner_url,
        )

        self._repository.save(video)
        logger.info(f"Video with id {input.id} saved")
