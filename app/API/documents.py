from fastapi import APIRouter, status, Depends, HTTPException
from app.core.schemas.document import Document, PaginatedDocument
from app.core.models.document_data import DocumentData
from app.core.models.user_data import UserData
from app.dbs import document_collection, user_collection
from app.API.users import get_current_user
from app.core.schemas.user import User, PaginatedUser
from app.core.models.visibility_data import VisibilityData
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from typing import List
import re

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

    if document.title == "":
        raise bad_request_exception

    new_document = {
        "title": document.title,
        "content": document.content,
        "author": current_user["username"],
        "editors": [],
        "public": True,
        "creation_date": datetime.now()
    }

    _id = document_collection.insert_one(new_document)
    new_document["id"] = _id.inserted_id
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
    if not edit_document["author"] == current_user["username"] and not current_user["username"] in edit_document["editors"]:
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

    if not delete_document["author"] == current_user["username"]:
        raise forbidden_exception
    
    document_collection.delete_one({"_id": delete_document["_id"]})

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
    if get_document["public"] == False and not get_document["author"] == current_user["username"] and not current_user["username"] in get_document["editors"]:
        raise forbidden_exception

    return get_document

@router.put(
    "/{document_id}/visibility", 
    status_code = status.HTTP_200_OK,
    response_model = Document
)
async def change_document_visibility_by_id(
        document_id: str,
        visibility: VisibilityData,
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
    if not edit_document["author"] == current_user["username"]:
        raise forbidden_exception    

    return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$set': { "public" :  visibility.public} },  return_document = ReturnDocument.AFTER)
    return return_document



@router.get(
    "/search", 
    status_code = status.HTTP_200_OK,
    response_model = PaginatedDocument
)
async def search_document(
        search: str,
        page: int = 1,
        page_size: int = 10,
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

    get_documents = document_collection.find(search_request).sort("creation_date", -1).skip((page - 1) * page_size).limit(page_size)
    if get_documents is None:
        raise not_found_exception

    return PaginatedDocument(
        current_page = page,
        total_pages = document_collection.count_documents(search_request) // page_size + 1,
        page_size = page_size,
        documents = [Document(**document) for document in get_documents]
    )
#TODO probar paginado

@router.put(
    "/{document_id}/editors", 
    status_code = status.HTTP_200_OK,
    response_model = Document
)
async def change_document_editor_by_username(
        document_id: str,
        editor: UserData,
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
    if not edit_document["author"] == current_user["username"]:
        raise forbidden_exception  

    subject_editor = user_collection.find_one({"username": editor.username})
    if subject_editor is None:
        raise user_not_found_exception
        
    if subject_editor in edit_document["editors"]:
        return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$pull': { "editors" :  subject_editor["username"]} },  return_document = ReturnDocument.AFTER)
    elif not subject_editor == edit_document["author"]:
        return_document = document_collection.find_one_and_update({"_id": ObjectId(document_id)}, { '$push': { "editors" :  subject_editor["username"]} },  return_document = ReturnDocument.AFTER)
    else:
        raise editor_is_author_exception
    return return_document

@router.get(
    "/{document_id}/editors", 
    status_code = status.HTTP_200_OK,
    response_model = PaginatedUser
)
async def get_document_editors(
        document_id: str,
        page: int = 1,
        page_size: int = 10,
        current_user: User = Depends(get_current_user)
    ):

    document_not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specified document not found"
    )

    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to view the editors of this document"
    )

    edit_document = document_collection.find_one({"_id": ObjectId(document_id)})
    if edit_document is None:
        raise document_not_found_exception
    if not edit_document["author"] == current_user["username"] and not current_user["username"] in edit_document["editors"] and edit_document["public"] == False:
        raise forbidden_exception  
        
    return PaginatedUser(
        current_page = page,
        total_pages = len(edit_document["editors"]) // page_size + 1,
        page_size = page_size,
        users = [str(**user) for user in edit_document["editors"]]
    )

@router.put(
"/{document_id}/favourite", 
status_code = status.HTTP_200_OK
)
async def change_document_editor_by_username(
        document_id: str,
        current_user: User = Depends(get_current_user)
    ):

    document_not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specified document not found"
    )

    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to view this document"
    )

    fav_document = document_collection.find_one({"_id": ObjectId(document_id)})
    if fav_document is None and ObjectId(document_id) in current_user["favourites"]:
        user_collection.update_one({'username': current_user["username"]},{'$pull': {'favourites': ObjectId(document_id)}})
        return {}
    elif fav_document is None: 
        raise document_not_found_exception
    if fav_document["public"] == False and not fav_document["author"] == current_user["username"] and not current_user in fav_document["editors"]:
        raise forbidden_exception  
        

    if fav_document["_id"] in current_user["favourites"]:
        user_collection.update_one({'username': current_user["username"]},{'$pull': {'favourites': fav_document["_id"]}})
    else :
        user_collection.update_one({'username': current_user["username"]},{'$push': {'favourites': fav_document["_id"]}})
    
    return {}