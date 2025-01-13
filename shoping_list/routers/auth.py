from datetime import timedelta, datetime, timezone
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import status
from models import Users
from pydantic import BaseModel
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from utils.auth_utils import *


router= APIRouter(
  prefix='/auth',
  tags=['auth']
)

def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()


class CreateUserRequest(BaseModel):
  username: str
  password: str
  email: str

class Token(BaseModel):
  access_token: str
  token_type: str

def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()


db_dependency=Annotated[Session,Depends(get_db)]

@router.post('/', status_code=status.HTTP_201_CREATED )
async def create_user(db: db_dependency, create_user_request:CreateUserRequest):
  if validate_password(create_user_request.password) == False :
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password ")
  if validate_email(create_user_request.email) == False:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid  email")
  create_user_model= Users(
    username=create_user_request.username,
    password_hash=bcrypt_context.hash(create_user_request.password),
    email=create_user_request.email
  )
  db.add(create_user_model)
  db.commit()

@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db : db_dependency):
  user=authenticate_user(form_data.username, form_data.password, db)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
  access_token_expires=timedelta(minutes=30)
  access_token=create_access_token(user.username, user.id, access_token_expires)
  return {"access_token": access_token, "token_type": "bearer"}
  