from fastapi import FastAPI

from src.infra.api.http.category_router import router as category_router
from src.infra.api.http.cast_member_router import router as cast_member_route

app = FastAPI()
app.include_router(category_router, prefix="/categories")
app.include_router(cast_member_route, prefix="/cast_members")


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}
