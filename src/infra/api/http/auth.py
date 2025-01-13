import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
public_key = f"-----BEGIN PUBLIC KEY-----\n{os.getenv('KEYCLOAK_PUBLIC_KEY', '')}\n-----END PUBLIC KEY-----\n"


def authenticate(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> None:
    try:
        jwt.decode(jwt=credentials.credentials, key=public_key, algorithms=["RS256"], audience="account")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token.'
        )
