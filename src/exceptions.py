from fastapi.exceptions import HTTPException


class BibiliotecaException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class PasswordTooShortException(BibiliotecaException):
    detail = "Пароль слишком короткий"


################################# ALREADY EXISTS EXCEPTIONS #################################


class ObjectAlreadyExistsException(BibiliotecaException):
    detail = "Объект уже существует"


class UserAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Пользователь уже существует"


################################# NOT FOUND EXCEPTIONS #################################


class ObjectNotFoundException(BibiliotecaException):
    detail = "Объект не найден"


class UserNotFoundException(ObjectNotFoundException):
    detail = "Пользователь не найден"


################################# HTTP EXCEPTIONS #################################


class BibliotecaHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self, *args, **kwargs):
        super().__init__(self.status_code, self.detail, *args, **kwargs)


class UserAlreadyExistsHTTPException(BibliotecaHTTPException):
    status_code = 409
    detail = "Пользователь с таким email уже существует"


class PasswordTooShortHTTPException(BibliotecaHTTPException):
    status_code = 422
    detail = "Пароль слишком короткий"
