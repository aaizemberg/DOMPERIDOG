from pydantic import BaseModel
from datetime import date
from app.core.schemas.user import User
from typing import List

class Document(BaseModel):
    title: str
    content: str
    author: User
    editors: List[User]
    public: bool
    creation_date: date

class PaginatedDocument(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    documents: List[Document]