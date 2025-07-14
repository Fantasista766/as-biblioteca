from datetime import date

from fastapi import APIRouter, Query

from src.api.decorators import cache
from src.api.dependecies import DBDep, PaginationDep
from src.schemas.books import BookDTO
from src.services.books import BookService

router = APIRouter(prefix="/books", tags=["Книги"])


@router.get(
    "/",
    summary="Получить фильтрованный список книг",
)
@cache(expire=10)
async def get_books(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название книги"),
    author: str | None = Query(None, description="Автор книги"),
    date_from: date = Query(example="2025-06-19"),
    date_to: date = Query(example="2025-06-29"),
) -> list[BookDTO]:
    return await BookService(db).get_filtered_by_time(pagination, title, author, date_from, date_to)
