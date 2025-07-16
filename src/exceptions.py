from fastapi.exceptions import HTTPException


class BibiliotecaException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class InvalidJWTException(BibiliotecaException):
    detail = "Неверный токен"


class PasswordTooShortException(BibiliotecaException):
    detail = "Пароль слишком короткий"


class UserAlreadyLoggedOutException(BibiliotecaException):
    detail = "Вы ещё не аутентифицированы"


class WrongPasswordException(BibiliotecaException):
    detail = "Неверный пароль"


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


class InvalidJWTHTTPException(BibliotecaHTTPException):
    status_code = 401
    detail = "Неверный токен"


class PasswordTooShortHTTPException(BibliotecaHTTPException):
    status_code = 422
    detail = "Пароль слишком короткий"


class UserAlreadyExistsHTTPException(BibliotecaHTTPException):
    status_code = 409
    detail = "Пользователь с таким email уже существует"


class UserAlreadyLoggedOutHTTPException(BibliotecaHTTPException):
    status_code = 409
    detail = "Вы ещё не аутентифицированы"


class UserNotFoundHTTPException(BibliotecaHTTPException):
    status_code = 404
    detail = "Пользователь не найден"


class WrongPasswordHTTPException(BibliotecaHTTPException):
    status_code = 401
    detail = "Неверный пароль"
