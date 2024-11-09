import logging

from elasticsearch import Elasticsearch
from pydantic_core._pydantic_core import ValidationError

from src.category import Category
from src.category_repository import (
    CategoryRepository,
    DEFAULT_PAGINATION_SIZE,
    SortDirection,
)

CATEGORY_INDEX = "catalog-db.codeflix.categories"


class ElasticsearchCategoryRepository(CategoryRepository):

    def __init__(self, client: Elasticsearch | None = None) -> None:
        self.client = client or Elasticsearch(hosts=["http://localhost:9200"])

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
        response = self.client.search(
            index=CATEGORY_INDEX,
            body=None,  # TODO: adicionar query para busca/ordenação/paginação
        )
        category_hits = response["hits"]["hits"]

        parsed_categories = []
        for category in category_hits:
            try:
                parsed_category = Category(**category["_source"])
            except ValidationError as e:
                logging.error(f"Malformed category: {category["_source"]}")
            else:
                parsed_categories.append(parsed_category)

        return parsed_categories
