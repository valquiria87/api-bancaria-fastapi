
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "Configure a variável de ambiente JWT_SECRET_KEY antes de iniciar a API."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def criar_token(dados: dict) -> str:
    dados_token = dados.copy()
    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    dados_token.update({"exp": expira_em})

    return jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


async def verificar_token(token: str = Depends(oauth2_scheme)) -> dict:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        if not payload.get("sub"):
            raise credenciais_invalidas
        return payload
    except jwt.InvalidTokenError:
        raise credenciais_invalidas
