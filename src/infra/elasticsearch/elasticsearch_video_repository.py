import logging

from elasticsearch import Elasticsearch, NotFoundError
from pydantic import ValidationError

from src.application.list_video import VideoSortableFields
from src.application.listing import DEFAULT_PAGINATION_SIZE, SortDirection
from src.domain.video import Video
from src.domain.video_repository import VideoRepository
from src.infra.elasticsearch import ELASTICSEARCH_HOST


class ElasticsearchVideoRepository(VideoRepository):
    INDEX = "catalog-db.codeflix.videos"

    def __init__(
        self,
        client: Elasticsearch | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._client = client or Elasticsearch(hosts=[ELASTICSEARCH_HOST])
        self._logger = logger or logging.getLogger(__name__)

    def search(
        self,
        page: int = 1,
        per_page: int = DEFAULT_PAGINATION_SIZE,
        search: str | None = None,
        sort: VideoSortableFields | None = None,
        direction: SortDirection = SortDirection.ASC,
    ) -> list[Video]:
        query = {
            "from": (page - 1) * per_page,
            "size": per_page,
            "sort": [{f"{sort}.keyword": {"order": direction}}] if sort else [],
            "query": {
                "bool": {
                    "must": (
                        [{"multi_match": {"query": search, "fields": ["title"]}}]
                        if search
                        else [{"match_all": {}}]
                    )
                }
            },
        }

        try:
            hits = self._client.search(
                index=self.INDEX,
                body=query,
            )["hits"]["hits"]
        except NotFoundError:
            self._logger.error(f"Index {self.INDEX} not found")
            return []

        parsed_entities = []
        for hit in hits:
            try:
                parsed_entity = Video(**hit["_source"])
            except ValidationError:
                self._logger.error(f"Malformed entity: {hit}")
            else:
                parsed_entities.append(parsed_entity)

        return parsed_entities

    def save(self, video: Video) -> None:
        self._client.index(
            index=self.INDEX,
            id=str(video.id),
            body=video.model_dump(mode="json"),
        )
