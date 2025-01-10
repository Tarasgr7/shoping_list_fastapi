from datetime import timedelta, datetime, timezone
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import status
from ..models import Users
from pydantic import BaseModel
from ..database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session


router= APIRouter(
  prefix='/auth',
  tags=['auth']
)
SECRET_KEY="126474140cdf5d05dab0a5cd0809d207d48095d8e459ff7515ec722b281cba8e"
ALGORITHM='HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')

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

def authenticate_user(username:str,password:str, db):
  user= db.query(Users).filter(Users.username==username).first()
  if not user:
    return False
  if not bcrypt_context.verify(password, user.password_hash):
    return False
  return user

def create_access_token(username:str,user_id: int, expires_data: timedelta):
  encode= {'sub':username,'id':user_id}
  expires=datetime.now() + expires_data
  encode.update({'exp':expires})
  return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
  try:
    payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username=payload.get('sub')
    user_id=payload.get('id')
    if username is None or user_id is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    return {'username': username,'user_id': user_id}
  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@router.post('/', status_code=status.HTTP_201_CREATED )
async def create_user(db: db_dependency, create_user_request:CreateUserRequest):
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
  