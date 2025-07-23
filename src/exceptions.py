from fastapi.exceptions import HTTPException


class BibliotecaException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class InvalidJWTException(BibliotecaException):
    detail = "Неверный токен"


class JWTMissingException(BibliotecaException):
    detail = "Токен отсутствует"


class PasswordTooShortException(BibliotecaException):
    detail = "Пароль слишком короткий"


class UserAlreadyLoggedInException(BibliotecaException):
    detail = "Вы уже аутентифицированы"


class UserAlreadyLoggedOutException(BibliotecaException):
    detail = "Вы ещё не аутентифицированы"


class WrongPasswordException(BibliotecaException):
    detail = "Неверный пароль"


################################# ALREADY EXISTS EXCEPTIONS #################################


class ObjectAlreadyExistsException(BibliotecaException):
    detail = "Объект уже существует"


class UserAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Пользователь с таким Email уже существует"


################################# NOT FOUND EXCEPTIONS #################################


class ObjectNotFoundException(BibliotecaException):
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


class JWTMissingHTTPException(BibliotecaHTTPException):
    status_code = 401
    detail = "Токен отсутствует"


class PasswordTooShortHTTPException(BibliotecaHTTPException):
    status_code = 422
    detail = "Пароль слишком короткий"


class UserAlreadyExistsHTTPException(BibliotecaHTTPException):
    status_code = 409
    detail = "Пользователь с таким email уже существует"


class UserAlreadyLoggedInHTTPException(BibliotecaHTTPException):
    status_code = 409
    detail = "Вы уже аутентифицированы"


class UserAlreadyLoggedOutHTTPException(BibliotecaHTTPException):
    status_code = 409
    detail = "Вы ещё не аутентифицированы"


class UserNotFoundHTTPException(BibliotecaHTTPException):
    status_code = 404
    detail = "Пользователь не найден"


class WrongPasswordHTTPException(BibliotecaHTTPException):
    status_code = 401
    detail = "Неверный пароль"
