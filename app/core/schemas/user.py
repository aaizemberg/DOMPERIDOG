from pydantic import BaseModel
from typing import List

class User(BaseModel):
    username: str
    favourites: list(str)

class UserInDB(User):
    hashed_password: str

class PaginatedUser(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    users: List[User]