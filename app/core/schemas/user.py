from pydantic import BaseModel, Field
from typing import List
from core.models.object_id import PyObjectId

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    favourites: List[str]

class UserInDB(User):
    hashed_password: str

class PaginatedUser(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    users: List[str]