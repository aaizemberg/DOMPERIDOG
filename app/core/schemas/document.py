from pydantic import BaseModel
from datetime import date
from app.core.schemas.user import User
from typing import List

class Document(BaseModel):
    id:str
    title: str
    content: str
    author: str
    editors: List[str]
    public: bool
    creation_date: date

class PaginatedDocument(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    documents: List[Document]

class PaginatedDocumentFav(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    documents: List[str]