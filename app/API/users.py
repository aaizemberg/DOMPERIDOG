from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.settings import settings
from app.core.schemas.user import User
from app.core.schemas.document import Document
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
        response_model = User, 
        status_code = status.HTTP_200_OK
    )
async def get_current_user_profile(
        current_user: User = Depends(get_current_user)
    ):
    return current_user

@router.get(
        "/{username}", 
        response_model = User, 
        status_code = status.HTTP_200_OK
    )
async def get_user_by_username(
        username: str, 
        current_user: User = Depends(get_current_user)
    ):
    if(current_user["username"] == username):
        return current_user
    else:
        
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You don not have permission to use this resource",
                )


@router.get(
        "/{username}/favourites", 
        response_model = List[Document], 
        status_code = status.HTTP_200_OK
    )
async def get_user_favourites_by_username(
        username: str, 
        current_user: User = Depends(get_current_user)
    ):
    if(current_user["username"] == username):
        links = List(document_collection.find({"author.username": username}).sort("creation_date", -1))
        return links
    else:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You don not have permission to use this resource",
            )

@router.post(
        "", 
        status_code = status.HTTP_201_CREATED,
        response_model = User
    )
async def register(
        user: UserCredentials
    ):
    new_user = {
        "username": user.username,
        "password": pwd_hasher.hash(user.password)
    }

    user = user_collection.find_one({"username": new_user["username"]})

    if user:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Specified username already exists"
            )

    user_collection.insert_one(new_user)
    return new_user
	    

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