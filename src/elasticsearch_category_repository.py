import logging
import os

from elasticsearch import Elasticsearch
from pydantic import ValidationError

from src.category import Category
from src.category_repository import (
    CategoryRepository,
    DEFAULT_PAGINATION_SIZE,
    SortDirection,
)

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ELASTICSEARCH_HOST_TEST = os.getenv("ELASTICSEARCH_TEST_HOST", "http://localhost:9201")


class ElasticsearchCategoryRepository(CategoryRepository):
    INDEX = "catalog-db.codeflix.categories"

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
        sort: str | None = None,
        direction: SortDirection = SortDirection.ASC,
    ) -> list[Category]:
        # Se quiséssemos o total de resultados, poderíamos usar o campo "total" do response
        # total_count = response["hits"]["total"]["value"]
        # pode ser utilizado pra calcular a "next_page" por exemplo.
        query = {
            "from": (page - 1) * per_page,
            "size": per_page,
            "sort": [{f"{sort}.keyword": {"order": direction}}] if sort else [],
            "query": {
                "bool": {
                    "must": (
                        [{"multi_match": {"query": search, "fields": ["name", "description"]}}]
                        if search
                        else [{"match_all": {}}]
                    )
                }
            },
        }

        response = self._client.search(
            index=self.INDEX,
            body=query,
        )
        category_hits = response["hits"]["hits"]

        parsed_categories = []
        for category in category_hits:
            try:
                parsed_category = Category(**category["_source"])
            except ValidationError:
                self._logger.error(f"Malformed category: {category}")
            else:
                parsed_categories.append(parsed_category)

        return parsed_categories
