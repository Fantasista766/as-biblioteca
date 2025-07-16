from typing import Annotated

from fastapi import Depends

from src.config import settings
from src.utils.db_manager import DBManager


def get_db_manager():
    return DBManager(db_url=settings.DB_URL, db_name=settings.DB_NAME)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
