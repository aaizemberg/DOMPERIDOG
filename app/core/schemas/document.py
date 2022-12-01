from pydantic import BaseModel, Field
from datetime import date
from typing import List
from app.core.models.object_id import PyObjectId
from bson.objectid import ObjectId


class Document(BaseModel):
    title: str
    content: str
    author: str
    editors: List[str]
    public: bool
    creation_date: date

class DocumentExt(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PaginatedDocument(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    documents: List[DocumentExt]

class PaginatedDocumentFav(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    documents: List[str]