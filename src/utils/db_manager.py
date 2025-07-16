from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.repositories.users import UsersRepository


class DBManager:
    def __init__(self, db_url: str, db_name: str):
        self.client = AsyncIOMotorClient(db_url)
        self.db: AsyncIOMotorDatabase = self.client[db_name]

        self.users = UsersRepository(self.db)

    async def __aenter__(self) -> "DBManager":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.client.close()

    async def init_indexes(self):
        await self.db["users"].create_index("email", unique=True, name="unique_email_idx")
