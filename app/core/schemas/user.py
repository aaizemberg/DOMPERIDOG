from pydantic import BaseModel, Field
from typing import List
from app.core.models.object_id import PyObjectId
from bson.objectid import ObjectId

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    favourites: List[str]

class UserExt(User):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserInDB(User):
    hashed_password: str

class PaginatedUser(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    users: List[str]