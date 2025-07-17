from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserAddDTO(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    role: Literal["user", "admin", "author"]


class UserDTO(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: Literal["user", "admin", "author"]


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserPutDTO(UserLoginDTO):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)


class UserPutRequest(BaseModel):
    email: EmailStr
    hashed_password: str
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)


class UserRegisterDTO(UserPutDTO):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    role: Literal["user", "admin", "author"] = "user"


class UserWithHashedPasswordDTO(UserDTO):
    hashed_password: str
