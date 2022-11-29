from fastapi import APIRouter, status
from app.core.schemas.document import Document
from app.core.models.document_data import DocumentData
from app.dbs import document_collection

router = APIRouter()

@router.post(
        "", 
        status_code = status.HTTP_201_CREATED,
        response_model = Document
    )
async def create_document(
        document: DocumentData
    ):
    new_document = {
        "title": document.title,
        "content": document.content
    }

    document_collection.insert_one(new_document)
    return new_document