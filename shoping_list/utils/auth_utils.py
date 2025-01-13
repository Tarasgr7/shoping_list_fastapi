
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import  HTTPException, Depends, status
from typing import Annotated
from models import Users
from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt
import re

SECRET_KEY="126474140cdf5d05dab0a5cd0809d207d48095d8e459ff7515ec722b281cba8e"

ALGORITHM='HS256'

def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()


bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')


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



def validate_password(password):
    """
    Перевіряє пароль на відповідність вимогам:
    - Містить малі англійські літери
    - Містить великі англійські літери
    - Містить цифри
    - Містить спеціальні символи

    :param password: str, пароль користувача
    :return: dict, результат перевірки
    """
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    return has_lowercase and has_uppercase and has_digit and has_special

def validate_email(email):
    """
    Перевіряє, чи відповідає email стандартному формату.

    :param email: str, email користувача
    :return: bool, True якщо email валідний, інакше False
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))