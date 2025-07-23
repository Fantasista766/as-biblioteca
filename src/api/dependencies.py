from typing import Annotated, Callable

from fastapi import Depends, Request

from src.abac import access_manager
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


async def _get_subject(request: Request) -> dict[str, any]:
    token = await get_token(request)
    data = AuthService().decode_token(token)
    user = await AuthService().get_user(data["user_id"])
    return {"id": user.id, "role": user.role}


def abac_required(action, resource_getter: Callable[[Request], dict[str, any]] | None = None):
    async def is_permitted(request: Request) -> bool:
        subject = await _get_subject(request)
        resource = resource_getter(request) if resource_getter else {}
        if not access_manager.check(action, subject, resource):
            raise PermissionError
        return True

    return Annotated[bool, Depends(is_permitted)]


EditUserPermissionDep = abac_required("user:edit")
