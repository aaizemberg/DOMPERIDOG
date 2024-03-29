from pydantic import BaseModel, Field as PydanticField
from datetime import date
from typing import List, Dict
from app.core.models.object_id import PyObjectId
from bson.objectid import ObjectId
import pydantic
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

class Document(BaseModel):
    title: str
    content: str
    emoji: str
    author: str
    editors: List[str]
    public: bool
    creation_date: date
    id: PyObjectId = PydanticField(default_factory=PyObjectId, alias="_id")
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PaginatedDocument(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    documents: List[Document]
