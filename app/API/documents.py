from fastapi import APIRouter, status, Depends, HTTPException
from app.core.schemas.document import Document
from app.core.models.document_data import DocumentData
from app.dbs import document_collection
from app.API.users import get_current_user
from app.core.schemas.user import User
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument

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

@router.put(
        "/{document_id}", 
        status_code = status.HTTP_200_OK,
        response_model = Document
    )
async def create_document(
        document_id: str,
        document: DocumentData,
        current_user: User = Depends(get_current_user)
    ):

    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specified document not found"
    )

    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to edit this document"
    )

    edit_document = document_collection.find_one({"_id": ObjectId(document_id)})
    if edit_document is None:
        raise not_found_exception
    if not edit_document["author"] == current_user and not current_user in edit_document["editors"]:
        raise forbidden_exception

    return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$set': { "title" :  document.title, "content": document.content} },  return_document = ReturnDocument.AFTER)
    return return_document