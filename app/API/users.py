from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.settings import settings
from app.core.schemas.user import User, UserInDB
from app.core.schemas.document import PaginatedDocument, Document
from app.core.models.user_credentials import UserCredentials
from app.dbs import user_collection, document_collection
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List
from bson.objectid import ObjectId
import re

pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
router = APIRouter()

@router.post(
        "", 
        status_code = status.HTTP_201_CREATED,
        response_model = User
    )
async def register(
        user: UserCredentials
    ):

    not_valid_password = HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Password is not valid. Must contain 1 upper letter, 1 lower letter, 1 number and be at least 8 characters long"
    )

    not_valid_username = HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Username must be at least 4 characters long and contain only alphanumeric characters, underscores, periods, and dashes",
    )

    if not is_valid_password(user.password):
      raise not_valid_password

    if not is_valid_username(user.username):
        raise not_valid_username

    new_user = {
        "username": user.username,
        "password": pwd_hasher.hash(user.password),
        "favourites": []
    }

    user = user_collection.find_one({"username": new_user["username"]})

    if user:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Specified username already exists"
            )

    _id = user_collection.insert_one(new_user)
    new_user["id"] = _id.inserted_id
    return new_user

async def get_current_user(
        jwt_token: str = Depends(oauth2_scheme)
    ):

    bad_credentials_exception = HTTPException(
        headers={"WWW-Authenticate": "Bearer"},
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Bad credentials - could not validate"
    )

    try:
        jwt_payload = jwt.decode(jwt_token, settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_SIGNATURE_ALGORITHM])

        username: str = jwt_payload.get("sub")

        if username is None:
            raise bad_credentials_exception

    except JWTError:
        raise bad_credentials_exception

    user = user_collection.find_one({"username": username})
    if user is None:
        raise bad_credentials_exception
    return user

@router.get(
        "/me", 
        response_model = UserInDB, 
        status_code = status.HTTP_200_OK
    )
async def get_current_user_profile(
        current_user: User = Depends(get_current_user)
    ):
    return current_user

@router.get(
        "/me/documents", 
        response_model = PaginatedDocument, 
        status_code = status.HTTP_200_OK
    )
async def get_current_user_documents( 
        current_user: User = Depends(get_current_user),
        page: int = 1,
        page_size: int = 10,

    ):
    get_documents = list(document_collection.find({"author": current_user["username"]}).sort("creation_date", -1).skip((page - 1) * page_size).limit(page_size))
    documents = [Document(**document) for document in get_documents]

    return PaginatedDocument(
        current_page = page,
        total_pages =  document_collection.count_documents({"author": current_user["username"]}) // page_size + 1,
        page_size = page_size,
        documents = documents
    )

@router.get(
    "/me/favourites", 
    response_model = PaginatedDocument, 
    status_code = status.HTTP_200_OK
)
async def get_current_user_favourites( 
        current_user: User = Depends(get_current_user),
        page: int = 1,
        page_size: int = 10,
    ):
    get_documents = document_collection.find({"_id": {"$in": current_user["favourites"]}}).sort("creation_date", -1).skip((page - 1) * page_size).limit(page_size)
    documents = [Document(**document) for document in get_documents]
    
    return PaginatedDocument(
        current_page = page,
        total_pages = document_collection.count_documents({"_id": {"$in": current_user["favourites"]}}) // page_size + 1,
        page_size = page_size,
        documents = documents
    )


@router.delete(
        "", 
        status_code = status.HTTP_200_OK
    )
async def delete_user_by_username(
        current_user: User = Depends(get_current_user),
    ):
    documents = document_collection.find({"author": current_user["username"]})
    for document in documents:
        document_collection.delete_one({"_id": document["_id"]})
    user_collection.delete_one({"username": current_user["username"]})
    return {}


def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False

    if not re.search("[a-z]", password):
        return False

    if not re.search("[A-Z]", password):
        return False

    if not re.search("[0-9]", password):
        return False

    return True

def is_valid_username(username: str) -> bool:
    if len(username) < 4:
        return False

    if not re.search("^[a-zA-Z0-9_.-]+$", username):
        return False

    return True
