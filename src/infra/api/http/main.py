from fastapi import FastAPI, Depends, Query

from src.application.list_category import (
    ListCategory,
    ListCategoryInput,
    CategorySortableFields,
)
from src.application.listing import ListOutput, DEFAULT_PAGINATION_SIZE, SortDirection
from src.domain.category import Category
from src.domain.category_repository import CategoryRepository
from src.infra.elasticsearch.elasticsearch_category_repository import (
    ElasticsearchCategoryRepository,
)

app = FastAPI()


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}


def get_category_repository() -> CategoryRepository:
    # Vamos deixar aqui por simplicidade, mas isso poderia ser um arquivo separado de configuração, dependências, etc.
    return ElasticsearchCategoryRepository()


@app.get("/categories", response_model=ListOutput[Category])
def list_categories(
    repository: ElasticsearchCategoryRepository = Depends(get_category_repository),
    search: str | None = Query(None, description="Search term for name or description"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        DEFAULT_PAGINATION_SIZE,
        ge=1,
        le=100,
        description="Number of items per page",
    ),
    sort: CategorySortableFields = Query(
        CategorySortableFields.NAME, description="Field to sort by"
    ),
    direction: SortDirection = Query(
        SortDirection.ASC, description="Sort direction (asc or desc)"
    ),
) -> ListOutput[Category]:
    return ListCategory(repository=repository).execute(ListCategoryInput(
        search=search,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
    ))
