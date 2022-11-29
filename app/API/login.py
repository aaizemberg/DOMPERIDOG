from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from app.core.models.token import Token
from app.API.users import pwd_hasher
from jose import jwt
from app.dbs import user_collection
from app.core.settings import settings
from typing import Union

router = APIRouter()

def verify_pwd(
        plain_pwd, 
        hashed_pwd
    ):
    return pwd_hasher.verify(plain_pwd, hashed_pwd)

def authenticate_user(
        username: str, 
        password: str
    ):
    user = user_collection.find_one({"username": username})
    if not user:
        return False
    if not verify_pwd(password, user["password"]):
        return False
    return user

def generate_access_token(
        payload: dict, 
        expiration: Union[timedelta, None] = None
    ):

    to_encode = payload.copy()

    if expiration:
        expiration_date = datetime.utcnow() + expiration
    else:
        expiration_date = datetime.utcnow() + timedelta(minutes=30)

    to_encode.update({"exp": expiration_date})

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_SIGNATURE_ALGORITHM)

@router.post(
        "", 
        response_model = Token, 
        status_code = 201
    )
async def login(
        login_form: OAuth2PasswordRequestForm = Depends()
    ):
    user = authenticate_user(login_form.username, login_form.password)
    if not user:
        raise HTTPException(
            headers={"WWW-Authenticate": "Bearer"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad credentials, incorrect username or password",
        )
    access_token = generate_access_token(
        payload={"sub": user["username"]}, expiration=timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}