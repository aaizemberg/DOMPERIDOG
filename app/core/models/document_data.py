from pydantic import BaseModel

class DocumentData(BaseModel):
    document_id: int
    title: str
    content: str

