from pydantic import BaseModel, EmailStr, Field

# TODO: ADD role to user


class UserAddDTO(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str


class UserDTO(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserRegisterDTO(UserLoginDTO):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)


class UserWithHashedPasswordDTO(UserDTO):
    hashed_password: str
