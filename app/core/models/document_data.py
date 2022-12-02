from pydantic import BaseModel

class DocumentData(BaseModel):
    title: str
    content: str
    emoji: str

