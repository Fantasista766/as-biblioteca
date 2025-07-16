from fastapi import APIRouter

from src.api.dependencies import DBDep
from src.exceptions import (
    PasswordTooShortException,
    PasswordTooShortHTTPException,
    UserAlreadyExistsException,
    UserAlreadyExistsHTTPException,
)
from src.schemas.users import UserRegisterDTO
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register", summary="Регистрация пользователя")
async def register_user(
    db: DBDep,
    user_data: UserRegisterDTO,
) -> dict[str, str]:
    try:
        await AuthService(db).register_user(user_data)
        return {"status": "OK"}
    except PasswordTooShortException:
        raise PasswordTooShortHTTPException
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException
