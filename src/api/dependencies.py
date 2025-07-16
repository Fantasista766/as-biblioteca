from typing import Annotated

from fastapi import Depends, Request

from src.config import settings
from src.exceptions import JWTMissingException, JWTMissingHTTPException
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


def get_db_manager():
    return DBManager(db_url=settings.DB_URL, db_name=settings.DB_NAME)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


async def get_token(request: Request) -> str:
    try:
        return AuthService().get_token(request)
    except JWTMissingException:
        raise JWTMissingHTTPException


async def get_current_user_id(token: str = Depends(get_token)) -> int:
    data = AuthService().decode_token(token)
    return data["user_id"]


UserIdDep = Annotated[int, Depends(get_current_user_id)]
