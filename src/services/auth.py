from passlib.context import CryptContext

from src.exceptions import ObjectAlreadyExistsException, UserAlreadyExistsException
from src.schemas.users import UserAddDTO, UserRegisterDTO
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

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
