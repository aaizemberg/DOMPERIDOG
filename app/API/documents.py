from fastapi import APIRouter, status, Depends, HTTPException
from app.core.schemas.document import Document
from app.core.models.document_data import DocumentData
from app.dbs import document_collection, user_collection
from app.API.users import get_current_user
from app.core.schemas.user import User
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from typing import List
import re
from app.core.models.editor_data import EditorData

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

    bad_request_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty",
        )

    new_document = {
        "title": document.title,
        "content": document.content,
        "author": current_user,
        "editors": [],
        "public": True,
        "creation_date": datetime.now()
    }

    if document.title == "":
        raise bad_request_exception
        
    document_collection.insert_one(new_document)
    return new_document

@router.put(
        "/{document_id}", 
        status_code = status.HTTP_200_OK,
        response_model = Document
    )
async def edit_document_by_id(
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

    new_title = document.title

    if document.title == "":
        new_title = edit_document["title"]
    

    return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$set': { "title" :  new_title, "content": document.content} },  return_document = ReturnDocument.AFTER)
    return return_document

@router.delete(
    "/{document_id}", 
    status_code = status.HTTP_200_OK,
)
async def delete_document_by_id(
        document_id: str,
        current_user: User = Depends(get_current_user)
    ):

    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specified document not found"
    )

    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to delete this document"
    )

    delete_document = document_collection.find_one({"_id": ObjectId(document_id)})
    if delete_document is None:
        raise not_found_exception

    if not delete_document["author"] == current_user:
        raise forbidden_exception
    
    document_collection.delete_one({"_id": delete_document["_id"]})

    return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$set': { "title" :  new_title, "content": document.content} },  return_document = ReturnDocument.AFTER)
    return {}

@router.get(
        "/{document_id}", 
        status_code = status.HTTP_200_OK,
        response_model = Document
    )
async def get_document_by_id(
        document_id: str,
        current_user: User = Depends(get_current_user)
    ):

    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specified document not found"
    )

    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to view this document"
    )

    get_document = document_collection.find_one({"_id": ObjectId(document_id)})
    if get_document is None:
        raise not_found_exception
    if get_document["public"] == False and not get_document["author"] == current_user and not current_user in get_document["editors"]:
        raise forbidden_exception

    return get_document

@router.put(
    "/{document_id}/visibility", 
    status_code = status.HTTP_200_OK,
    response_model = Document
)
async def change_document_visibility_by_id(
        document_id: str,
        visibility: bool,
        current_user: User = Depends(get_current_user)
    ):

    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specified document not found"
    )

    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to change the visibility of this document"
    )

    edit_document = document_collection.find_one({"_id": ObjectId(document_id)})
    if edit_document is None:
        raise not_found_exception
    if not edit_document["author"] == current_user:
        raise forbidden_exception    

    return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$set': { "public" :  visibility} },  return_document = ReturnDocument.AFTER)
    return return_document



@router.get(
    "/search", 
    status_code = status.HTTP_200_OK,
    response_model = List[Document]
)
async def search_document(
        search: str,
        current_user: User = Depends(get_current_user)
    ):

    search_expr = re.compile(f".*{search}.*", re.I)

    search_request = {
        '$and': [
            {'public': True}, 
            {'$or': [
                    {'author': {'$regex': search_expr}},
                    {'title': {'$regex': search_expr}},
                    {'content': {'$regex': search_expr}}
            ]}
        ]
    }

    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No documents match search request"
    )

    get_documents = List(document_collection.find(search_request).sort("creation_date", -1))
    if get_documents is None:
        raise not_found_exception

    return get_documents


@router.put(
"/{document_id}/editors", 
status_code = status.HTTP_200_OK,
response_model = Document
)
async def change_document_editor_by_username(
        document_id: str,
        editor_username: str,
        current_user: User = Depends(get_current_user)
    ):

    document_not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specified document not found"
    )

    user_not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specified user not found"
    )

    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to change the editors of this document"
    )

    editor_is_author_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="The author can not be an editor"
    )


    edit_document = document_collection.find_one({"_id": ObjectId(document_id)})
    if edit_document is None:
        raise document_not_found_exception
    if not edit_document["author"] == current_user:
        raise forbidden_exception  

    subject_editor = user_collection.find_one({"username": editor_username})
    if subject_editor is None:
        raise user_not_found_exception
        
    if subject_editor in edit_document["editors"]:
        return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$pull': { "editors" :  subject_editor} },  return_document = ReturnDocument.AFTER)
    elif not subject_editor == edit_document["author"]:
        return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$push': { "editors" :  subject_editor} },  return_document = ReturnDocument.AFTER)
    else:
        raise editor_is_author_exception
    return return_document