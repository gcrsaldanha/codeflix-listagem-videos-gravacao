import logging

from src.application.save_video import SaveVideoInput, SaveVideo
from src.domain.video import Rating
from src.infra.codeflix_client.http_client import HttpClient
from src.infra.elasticsearch.elasticsearch_video_repository import ElasticsearchVideoRepository
from src.infra.kafka.abstract_event_handler import AbstractEventHandler
from src.infra.kafka.parser import ParsedEvent

logger = logging.getLogger(__name__)


class VideoEventHandler(AbstractEventHandler):  # Similar to a View in Django
    def __init__(self, save_use_case: SaveVideo | None = None):
        self.save_use_case = save_use_case or SaveVideo(
            repository=ElasticsearchVideoRepository(),
            codeflix_client=HttpClient(),
        )

    def _handle_update_or_create(self, event: ParsedEvent) -> None:
        input = SaveVideoInput(
            id=event.payload["id"],
            title=event.payload["title"],
            launch_year=event.payload["launch_year"],
            rating=Rating(event.payload["rating"]),
            created_at=event.payload["created_at"],
            updated_at=event.payload["updated_at"],
            is_active=event.payload["is_active"],
        )
        self.save_use_case.execute(input=input)

    def handle_created(self, event: ParsedEvent) -> None:
        logger.info(f"Creating video with payload: {event.payload}")
        self._handle_update_or_create(event)

    def handle_updated(self, event: ParsedEvent) -> None:
        logger.info(f"Updating video with payload: {event.payload}")
        self._handle_update_or_create(event)

    def handle_deleted(self, event: ParsedEvent) -> None:
        print(f"Deleting video: {event.payload}")
        # TODO: implement delete use case
