from fastapi import APIRouter, Request, Response

from src.abac import access_manager
from src.api.decorators import cache
from src.api.dependencies import DBDep, EditUserPermissionDep, UserIdDep
from src.exceptions import (
    InvalidJWTException,
    InvalidJWTHTTPException,
    PasswordTooShortException,
    PasswordTooShortHTTPException,
    UserAlreadyExistsException,
    UserAlreadyExistsHTTPException,
    UserAlreadyLoggedInException,
    UserAlreadyLoggedInHTTPException,
    UserAlreadyLoggedOutException,
    UserAlreadyLoggedOutHTTPException,
    UserNotFoundException,
    UserNotFoundHTTPException,
    WrongPasswordException,
    WrongPasswordHTTPException,
)
from src.schemas.users import UserLoginDTO, UserRegisterDTO, UserPutDTO, UserPutAdminDTO
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


@router.post("/login", summary="Аутентификация пользователя")
async def login_user(
    db: DBDep,
    user_data: UserLoginDTO,
    request: Request,
    response: Response,
) -> dict[str, str]:
    try:
        access_token = await AuthService(db).login_user(request, user_data)
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token}
    except InvalidJWTException:
        raise InvalidJWTHTTPException
    except UserAlreadyLoggedInException:
        raise UserAlreadyLoggedInHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except WrongPasswordException:
        raise WrongPasswordHTTPException


@router.put("/edit_me", summary="Обновление своего профиля")
async def edit_me(
    db: DBDep,
    user_id: UserIdDep,
    user_data: UserPutDTO,
) -> dict[str, str]:
    try:
        await AuthService(db).edit_user(user_id, user_data)
        return {"status": "OK"}
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException


@router.put(
    "/edit_user", summary="Обновление профиля пользователя", dependencies=[EditUserPermissionDep]
)
async def edit_user(
    user_edit_email: str,
    db: DBDep,
    user_id: UserIdDep,
    user_data: UserPutAdminDTO,
) -> dict[str, str]:
    subject_role = await AuthService(db).get_user_role(user_id)
    subject = {"id": user_id, "role": subject_role}
    if not access_manager.check("user:edit", subject):
        raise PermissionError
    try:
        await AuthService(db).admin_edit_user(user_edit_email, user_data)
        return {"status": "OK"}
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException


@router.post("/logout", summary="Выход из системы")
async def logout_user(request: Request, response: Response):
    try:
        await AuthService().logout_user(request, response)
    except UserAlreadyLoggedOutException:
        raise UserAlreadyLoggedOutHTTPException
    return {"status": "OK"}


@router.get("/me", summary="☻ Мой профиль")
@cache(expire=10)
async def get_me(db: DBDep, user_id: UserIdDep):
    try:
        return await AuthService(db).get_user(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
