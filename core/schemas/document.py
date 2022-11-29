from pydantic import BaseModel
from datetime import date
from core.schemas.user import User
from typing import Union

class Document(BaseModel):
    title: str
    content: str
    author: User
    editors: list[User]
    public: bool
    creation_date: date

class PaginatedDocument(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    documents: list[Document]