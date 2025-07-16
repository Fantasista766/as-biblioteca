from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, get_origin, get_args
import hashlib
import inspect
import json

from pydantic import BaseModel

from src.init import redis_manager

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def cache(expire: int = 60) -> Any:
    signature = None

    def decorator(func: Any) -> Any:
        nonlocal signature
        signature = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 1) Собираем аргументы
            bound = signature.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            args_dict = bound.arguments

            # 2) Фильтруем «зависимости» и все не-примитивы
            def is_primitive(v: Any) -> bool:
                return (
                    isinstance(v, (str, int, float, bool, type(None)))
                    or (isinstance(v, (list, tuple)) and all(is_primitive(i) for i in v))
                    or (
                        isinstance(v, dict)
                        and all(isinstance(k, str) and is_primitive(v[k]) for k in v)
                    )
                )

            filtered_args = {}
            for name, val in args_dict.items():
                # оставляем только примитивы
                if is_primitive(val):
                    filtered_args[name] = val

            # 3) Генерируем ключ из отфильтрованных аргументов
            key_raw = (
                f"{func.__module__}.{func.__name__}|"
                f"{json.dumps(filtered_args, default=str, sort_keys=True)}"
            )
            key = hashlib.sha256(key_raw.encode()).hexdigest()

            # 4) Пытаемся взять из Redis
            cached = await redis_manager.get(key)
            if cached:
                payload = json.loads(cached)
                ret_ann = signature.return_annotation
                origin = get_origin(ret_ann)
                # список моделей
                if origin is list:
                    model_type = get_args(ret_ann)[0]
                    return [model_type.parse_obj(item) for item in payload]
                # одиночная модель
                if inspect.isclass(ret_ann) and issubclass(ret_ann, BaseModel):
                    return ret_ann.model_validate(payload[0])
                # всё остальное
                return payload

            # 5) Если нет — вызываем оригинал, сохраняем и возвращаем
            result = await func(*args, **kwargs)

            # сериализуем результат
            if isinstance(result, list):
                out = [
                    item.model_dump() if isinstance(item, BaseModel) else item for item in result
                ]
            else:
                out = [result.model_dump() if isinstance(result, BaseModel) else result]

            await redis_manager.set(key, json.dumps(out, default=str), expire)
            return result

        return wrapper  # type: ignore

    return decorator
