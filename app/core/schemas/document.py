from pydantic import BaseModel, Field
from datetime import date
from typing import List
from core.models.object_id import PyObjectId

class Document(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
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