from fastapi import Depends, APIRouter

from src.infra.api.http.auth import authenticate

router = APIRouter()


@router.get("/")
def auth(authenticated: None = Depends(authenticate)):
    return {"status": "ok"}
