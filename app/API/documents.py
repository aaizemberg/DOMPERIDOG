from fastapi import APIRouter, status, Depends
from app.core.schemas.document import Document
from app.core.models.document_data import DocumentData
from app.dbs import document_collection
from app.API.users import get_current_user
from app.core.schemas.user import User
from datetime import datetime

router = APIRouter()

@router.post(
        "", 
        status_code = status.HTTP_201_CREATED,
        response_model = Document
    )
async def create_document(
        document: DocumentData,
        current_user: User = Depends(get_current_user)
    ):
    new_document = {
        "title": document.title,
        "content": document.content,
        "author": current_user,
        "editors": [],
        "public": True,
        "creation_date": datetime.now()
    }

    document_collection.insert_one(new_document)
    return new_document