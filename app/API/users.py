from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.settings import settings
from app.core.schemas.user import User, UserExt
from app.core.schemas.document import PaginatedDocument, DocumentExt, PaginatedDocumentFav
from app.core.models.user_credentials import UserCredentials
from app.dbs import user_collection, document_collection
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List

pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

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
        response_model = UserExt, 
        status_code = status.HTTP_200_OK
    )
async def get_current_user_profile(
        current_user: User = Depends(get_current_user)
    ):
    return UserExt(**current_user)

@router.get(
        "/{username}", 
        response_model = UserExt, 
        status_code = status.HTTP_200_OK
    )
async def get_user_by_username(
        username: str, 
        current_user: User = Depends(get_current_user)
    ):
    if(current_user["username"] == username):
        return UserExt(**current_user)
    else:
        
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You don not have permission to use this resource",
                )


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
    get_documents = document_collection.find({"author": current_user["username"]}).sort("creation_date", -1).skip((page - 1) * page_size).limit(page_size)
    return PaginatedDocument(
        current_page = page,
        total_pages = document_collection.count_documents({"username": current_user["username"]}) // page_size + 1,
        page_size = page_size,
        documents = [DocumentExt(**document) for document in get_documents]
    )

@router.get(
    "/me/favourites", 
    response_model = PaginatedDocumentFav, 
    status_code = status.HTTP_200_OK
)
async def get_current_user_favourites( 
        current_user: User = Depends(get_current_user),
        page: int = 1,
        page_size: int = 10,
    ):
    documents = document_collection.find({"_id": {"$in": current_user["favourites"]}}).sort("creation_date", -1).skip((page - 1) * page_size).limit(page_size)
    return PaginatedDocumentFav(
        current_page = page,
        total_pages = document_collection.count_documents({"_id": {"$in": current_user["favourites"]}}) // page_size + 1,
        page_size = page_size,
        documents = [str(**document["_id"]) for document in documents]
    )

     

@router.post(
        "", 
        status_code = status.HTTP_201_CREATED,
        response_model = UserExt
    )
async def register(
        user: UserCredentials
    ):
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
    return UserExt(**new_user)
	    

@router.delete(
        "/{id}", 
        status_code = status.HTTP_200_OK
    )
async def delete_user_by_username(
        username: str, 
        current_user: User = Depends(get_current_user),
    ):
    if not current_user["username"] == username:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You don not have permission to use this resource"
            )
    documents = List(document_collection.find({"author.username": username}))
    for document in documents:
        document_collection.delete_one({"_id": document["_id"]})
    user_collection.delete_one({"username": username})
    return {}
