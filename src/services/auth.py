from datetime import datetime, timezone, timedelta
from typing import Any
import jwt

from fastapi import Request, Response
from passlib.context import CryptContext

from src.config import settings
from src.exceptions import (
    ObjectAlreadyExistsException,
    UserAlreadyExistsException,
    UserAlreadyLoggedOutException,
    WrongPasswordException,
)
from src.schemas.users import UserAddDTO, UserLoginDTO, UserRegisterDTO
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register_user(self, user_data: UserRegisterDTO) -> None:
        hashed_password = self.hash_password(user_data.password)
        new_user_data = UserAddDTO(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
        )
        try:
            await self.db.users.add(new_user_data)  # type: ignore
        except ObjectAlreadyExistsException:
            raise UserAlreadyExistsException

    async def login_user(self, user_data: UserLoginDTO) -> str:
        user = await self.db.users.get_user_with_hashed_password(email=user_data.email)  # type: ignore
        self.verify_password(user_data.password, user.hashed_password)
        return self.create_access_token({"user_id": user.id})

    async def logout_user(self, request: Request, response: Response) -> None:
        if "access_token" not in request.cookies:
            raise UserAlreadyLoggedOutException
        response.delete_cookie("access_token")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> None:
        if not self.pwd_context.verify(plain_password, hashed_password):
            raise WrongPasswordException

    def create_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(  # type: ignore
            to_encode, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
