from fastapi import FastAPI

from src.infra.api.http.cast_member_router import router as cast_member_router
from src.infra.api.http.category_router import router as category_router
from src.infra.api.http.genre_router import router as genre_router

app = FastAPI()
app.include_router(category_router, prefix="/categories")
app.include_router(cast_member_router, prefix="/cast_members")
app.include_router(genre_router, prefix="/genres")


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}
