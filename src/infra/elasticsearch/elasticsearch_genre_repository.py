import logging
from collections import defaultdict

from elasticsearch import Elasticsearch
from pydantic import ValidationError

from src.application.list_genre import GenreSortableFields
from src.application.listing import DEFAULT_PAGINATION_SIZE, SortDirection
from src.domain.genre import Genre
from src.domain.genre_repository import GenreRepository
from src.infra.elasticsearch import ELASTICSEARCH_HOST


class ElasticsearchGenreRepository(GenreRepository):
    INDEX = "catalog-db.codeflix.genres"
    _GENRE_CATEGORIES_INDEX = "catalog-db.codeflix.genre_categories"

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
        sort: GenreSortableFields | None = None,
        direction: SortDirection = SortDirection.ASC,
    ) -> list[Genre]:
        query = {
            "from": (page - 1) * per_page,
            "size": per_page,
            "sort": [{f"{sort}.keyword": {"order": direction}}] if sort else [],
            "query": {
                "bool": {
                    "must": (
                        [{"multi_match": {"query": search, "fields": ["name"]}}]
                        if search
                        else [{"match_all": {}}]
                    )
                }
            },
        }

        hits = self._client.search(
            index=self.INDEX,
            body=query,
        )["hits"]["hits"]

        genre_ids = [hit["_source"]["id"] for hit in hits]
        parsed_entities = []
        for hit in hits:
            try:
                parsed_entity = Genre(
                    **{
                        **hit["_source"],
                        "categories": set(),
                    }
                )
            except ValidationError:
                self._logger.error(f"Malformed entity: {hit}")
            else:
                parsed_entities.append(parsed_entity)

        return parsed_entities