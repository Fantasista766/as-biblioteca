from pydantic import BaseModel, Field


class BookAddDTO(BaseModel):
    title: str = Field(..., min_length=5)
    author: str = Field(..., min_length=5)


class BookDTO(BookAddDTO):
    id: int
