from fastapi import FastAPI, Depends

from src.application.list_category import ListCategory, ListCategoryInput
from src.application.listing import ListOutput
from src.domain.category import Category
from src.domain.category_repository import CategoryRepository
from src.infra.elasticsearch.elasticsearch_category_repository import ElasticsearchCategoryRepository

app = FastAPI()


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}


def get_category_repository() -> CategoryRepository:
    # Vamos deixar aqui por simplicidade, mas isso poderia ser um arquivo separado de configuração, dependências, etc.
    return ElasticsearchCategoryRepository()


@app.get("/categories", response_model=ListOutput[Category])
def list_categories(repository: CategoryRepository = Depends(get_category_repository)) -> ListOutput[Category]:
    return ListCategory(repository=repository).execute(ListCategoryInput())
