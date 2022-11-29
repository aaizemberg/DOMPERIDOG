from pydantic import BaseModel
from typing import Union

class User(BaseModel):
    user_id: int
    username: str

class UserInDB(User):
    hashed_password: str