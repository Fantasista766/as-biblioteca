from src.repositories.mappers.base import DataMapper
from src.schemas.users import UserDTO, UserWithHashedPasswordDTO


class UserDataMapper(DataMapper[UserDTO]):
    schema = UserDTO


class UserWithHashedPasswordDataMapper(DataMapper):
    schema = UserWithHashedPasswordDTO
