from pydantic import BaseModel
from typing import Union

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str