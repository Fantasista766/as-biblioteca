from bson import ObjectId
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from pymongo.errors import BulkWriteError, DuplicateKeyError

from src.exceptions import ObjectAlreadyExistsException, ObjectNotFoundException


class BaseRepository:
    collection_name: str

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[self.collection_name]

    async def get_filtered(self, *filters: dict[str, Any], **filter_by: Any) -> list[Any]:
        """
        Вернёт все документы, подходящие под объединённый фильтр.
        *filters — произвольные словари-фильтры, которые будут слиты вместе.
        **filter_by — дополнительные фильтры через kwargs.
        """
        query_filter: dict[str, Any] = {}
        for f in filters:
            query_filter.update(f)
        query_filter.update(filter_by)

        cursor = self.collection.find(query_filter)
        documents = await cursor.to_list(length=None)

        return [self.mapper.map_to_domain_entity(doc) for doc in documents]

    async def get_all(self, *args: Any, **kwargs: Any) -> list[Any]:
        return await self.get_filtered()

    async def get_batch_by_ids(self, ids_to_get: list[str]) -> list[Any] | None:
        """
        Вернёт список документов по их _id.
        ids_to_get — список строковых представлений ObjectId.
        """
        if not ids_to_get:
            return []

        object_ids = [ObjectId(i) for i in ids_to_get]

        cursor = self.collection.find({"_id": {"$in": object_ids}})
        documents = await cursor.to_list(length=len(object_ids))

        return [self.mapper.map_to_domain_entity(doc) for doc in documents]

    async def get_one_or_none(self, **filter_by: Any) -> Any:
        """
        Вернёт один документ по переданным ключам filter_by
        или None, если ничего не найдено.
        """
        document = await self.collection.find_one(filter_by)

        self.mapper.map_to_domain_entity(document)

    async def get_one(self, **filter_by: Any) -> Any:
        """
        Вернёт один документ по переданным ключам filter_by.
        Если не найден — бросит ObjectNotFoundException.
        """
        if "id" in filter_by:
            raw_id = filter_by.pop("id")
            filter_by["_id"] = ObjectId(raw_id)
        document = await self.collection.find_one(filter_by)
        if not document:
            raise ObjectNotFoundException

        return self.mapper.map_to_domain_entity(document)

    async def add(self, data: BaseModel) -> Any:
        """
        Вставляет документ и возвращает доменную сущность.
        При попытке вставить дубликат бросает ObjectAlreadyExistsException.
        """
        doc = data.model_dump()
        try:
            result = await self.collection.insert_one(doc)
        except DuplicateKeyError:
            raise ObjectAlreadyExistsException

        inserted = await self.collection.find_one({"_id": result.inserted_id})
        return self.mapper.map_to_domain_entity(inserted)

    async def add_batch(self, data: list[Any]) -> list[Any]:
        """
        Вставляет сразу несколько документов.
        Возвращает список доменных сущностей.
        В случае ошибки массовой записи бросает ObjectAlreadyExistsException.
        """
        docs = [item.model_dump() for item in data]
        try:
            result = await self.collection.insert_many(docs, ordered=False)
        except BulkWriteError:
            ObjectAlreadyExistsException

        # получаем вставленные документы по их _id (чтобы получить все поля, включая _id)
        inserted_ids = result.inserted_ids
        cursor = self.collection.find({"_id": {"$in": inserted_ids}})
        inserted_docs = await cursor.to_list(length=len(inserted_ids))

        return [self.mapper.map_to_domain_entity(doc) for doc in inserted_docs]

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by: Any) -> int:
        """
        Обновляет один документ по фильтру filter_by значениями из data.
        Сначала проверяет, что документ существует (через get_one), иначе бросает ObjectNotFoundException.
        Возвращает количество изменённых полей (modified_count).
        """
        if "id" in filter_by:
            raw_id = filter_by.pop("id")
            filter_by["_id"] = ObjectId(raw_id)
        update_data = data.model_dump(exclude_unset=exclude_unset)
        result = await self.collection.update_one(filter_by, {"$set": update_data})

        return result.modified_count

    async def delete(self, **filter_by: Any) -> int:
        """
        Удаляет один документ по фильтру filter_by.
        Сначала проверяет существование (через get_one),
        иначе бросает ObjectNotFoundException.
        Возвращает количество удалённых документов (0 или 1).
        """
        await self.get_one(**filter_by)
        result = await self.collection.delete_one(filter_by)
        return result.deleted_count

    async def delete_batch_by_ids(self, ids_to_delete: list[str]) -> int:
        """
        Удаляет несколько документов по их _id.
        ids_to_delete — список строковых представлений ObjectId.
        Возвращает число удалённых документов.
        """
        if not ids_to_delete:
            return 0

        object_ids = [ObjectId(i) for i in ids_to_delete]
        result = await self.collection.delete_many({"_id": {"$in": object_ids}})
        return result.deleted_count
