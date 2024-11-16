from fastapi import FastAPI

from src.application.list_category import ListCategory, ListCategoryInput
from src.application.listing import ListOutput
from src.domain.category import Category
from src.infra.elasticsearch.elasticsearch_category_repository import ElasticsearchCategoryRepository

app = FastAPI()


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}


@app.get("/categories", response_model=ListOutput[Category])
def list_categories():
    return ListCategory(repository=ElasticsearchCategoryRepository()).execute(ListCategoryInput())
