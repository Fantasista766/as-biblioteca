from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, get_origin, get_args
import hashlib
import inspect
import json

from fastapi import HTTPException
from pydantic import BaseModel

from src.init import redis_manager  # ваш асинхронный клиент с методами get/set

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def cache(expire: int = 60) -> Callable[[F], F]:
    signature = None

    def decorator(func: F) -> F:
        nonlocal signature
        signature = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 1) Собираем полный набор аргументов и приводим к детерминированной JSON-строке
            bound = signature.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            args_dict = bound.arguments
            key_raw = f"{func.__module__}.{func.__name__}|{json.dumps(args_dict, default=str, sort_keys=True)}"
            key = hashlib.sha256(key_raw.encode()).hexdigest()

            # 2) Пытаемся достать из Redis
            cached = await redis_manager.get(key)
            if cached:
                payload = json.loads(cached)
                # Определяем тип возвращаемых данных
                ret_ann = signature.return_annotation
                origin = get_origin(ret_ann)
                # a) Список Pydantic-моделей
                if origin is list:
                    model_type = get_args(ret_ann)[0]
                    return [model_type.parse_obj(item) for item in payload]
                # b) Одиночная модель
                if inspect.isclass(ret_ann) and issubclass(ret_ann, BaseModel):
                    return ret_ann.model_validate(payload[0])
                # c) Любой другой JSON-десериализуемый тип
                return payload

            # 3) Если в кэше нет — вызываем функцию, сохраняем в Redis
            result = await func(*args, **kwargs)
            if not result:
                raise HTTPException(status_code=404, detail="Data not found")

            # Сериализуем результат в список словарей/примитивов
            if isinstance(result, list):
                out = [
                    item.model_dump() if isinstance(item, BaseModel) else item for item in result
                ]
            else:
                out = [result.model_dump() if isinstance(result, BaseModel) else result]

            # Записываем в Redis
            await redis_manager.set(key, json.dumps(out, default=str), expire)
            return result

        return wrapper  # type: ignore

    return decorator
