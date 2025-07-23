from datetime import datetime, timezone, timedelta
from typing import Any
import jwt

from fastapi import Request, Response
from passlib.context import CryptContext

from src.config import settings
from src.exceptions import (
    InvalidJWTException,
    JWTMissingException,
    ObjectAlreadyExistsException,
    UserAlreadyExistsException,
    UserAlreadyLoggedInException,
    UserAlreadyLoggedOutException,
    UserNotFoundException,
    WrongPasswordException,
)
from src.schemas.users import (
    UserAddDTO,
    UserLoginDTO,
    UserRegisterDTO,
    UserPutAdminDTO,
    UserPutDTO,
    UserPutRequest,
)
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
            role=user_data.role,
        )
        try:
            await self.db.users.add(new_user_data)  # type: ignore
        except ObjectAlreadyExistsException:
            raise UserAlreadyExistsException

    async def login_user(self, request: Request, user_data: UserLoginDTO) -> str:
        if "access_token" in request.cookies:
            raise UserAlreadyLoggedInException
        user = await self.db.users.get_user_with_hashed_password(email=user_data.email)  # type: ignore
        self.verify_password(user_data.password, user.hashed_password)
        return self.create_access_token({"user_id": user.id, "role": user.role})

    async def logout_user(self, request: Request, response: Response) -> None:
        if "access_token" not in request.cookies:
            raise UserAlreadyLoggedOutException
        response.delete_cookie("access_token")

    async def edit_user(self, user_id: str, user_data: UserPutDTO) -> None:
        user = await self.db.users.get_one(id=user_id)
        if not user:
            raise UserNotFoundException

        hashed_password = self.hash_password(user_data.password)
        new_user_data = UserPutRequest(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
        )
        try:
            await self.db.users.edit(new_user_data, exclude_unset=True, id=user_id)
        except ObjectAlreadyExistsException:
            raise UserAlreadyExistsException

    async def admin_edit_user(self, user_email: str, user_data: UserPutAdminDTO) -> None:
        user = await self.db.users.get_one(email=user_email)
        if not user:
            raise UserNotFoundException

        try:
            await self.db.users.edit(user_data, exclude_unset=True, email=user_email)
        except ObjectAlreadyExistsException:
            raise UserAlreadyExistsException

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

    def get_token(self, request: Request) -> str:
        try:
            return request.cookies["access_token"]
        except KeyError:
            raise JWTMissingException

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, key=settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)  # type: ignore
        except jwt.exceptions.DecodeError as _:
            raise InvalidJWTException

    async def get_user_role(self, user_id: str) -> str:
        user = await self.db.users.get_one(id=user_id)  # type: ignore
        return user.role
