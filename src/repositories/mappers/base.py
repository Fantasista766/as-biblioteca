from typing import Generic, TypeVar, Type
from pydantic import BaseModel
from bson import ObjectId

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper(Generic[SchemaType]):
    schema: Type[SchemaType]

    @classmethod
    def map_to_domain_entity(cls, data: dict | None) -> SchemaType | None:
        if data is None:
            return None

        if "_id" in data:
            data["id"] = str(data.pop("_id"))

        return cls.schema.model_validate(data)

    @classmethod
    def map_to_persistence_entity(cls, data: BaseModel) -> dict:
        """
        Превращает Pydantic-модель в dict для вставки в Mongo.
        Конвертирует id → ObjectId и убирает лишние None.
        """
        raw = data.model_dump(exclude_none=True)

        if "id" in raw and raw["id"] is not None:
            raw["_id"] = ObjectId(raw.pop("id"))

        return raw
