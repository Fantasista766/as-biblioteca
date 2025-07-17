from typing import Any

from pydantic import EmailStr

from src.exceptions import UserNotFoundException
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    UserDataMapper,
    UserWithHashedPasswordDataMapper,
)
from src.schemas.users import UserWithHashedPasswordDTO


class UsersRepository(BaseRepository):
    collection_name = "users"
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr) -> UserWithHashedPasswordDTO:
        """
        Находит по email и возвращает DTO с полем hashed_password.
        Бросает UserNotFoundException, если не найден.
        """
        # Ищем документ, сразу проецируем только нужные поля
        document: dict[str, Any] | None = await self.collection.find_one(
            {"email": email},
            {
                "email": 1,
                "hashed_password": 1,
                "_id": 1,
                "first_name": 1,
                "last_name": 1,
                "role": 1,
            },
        )
        if not document:
            raise UserNotFoundException

        # Маппим документ в DTO
        return UserWithHashedPasswordDataMapper.map_to_domain_entity(document)
