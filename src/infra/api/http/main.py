from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI

from src.domain.category import Category

app = FastAPI()


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}


category = Category(
    id=uuid4(),
    name="Filme",
    description="Categoria de filmes",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    is_active=True,
)


@app.get("/categories")
def list_categories():
    return {"categories": [category]}
