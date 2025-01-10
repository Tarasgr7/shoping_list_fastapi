from fastapi import APIRouter,Depends,HTTPException,Path
from typing import Annotated
from pydantic import BaseModel
from ..database import SessionLocal
from sqlalchemy.orm import Session
from ..models import Users
from passlib.context import CryptContext
from fastapi import status
from .auth import get_current_user

router=APIRouter(
  prefix='/user',
  tags=['user']
)

def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency=Annotated[Session, Depends(get_db)]
user_dependency=Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
  password: str
  new_password: str

@router.get('/',status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency,db: db_dependency):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  return db.query(Users).filter(Users.id==user.get('user_id')).first()

@router.put('/password',status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency,db:db_dependency, user_verification: UserVerification):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  user_model=db.query(Users).filter(Users.id==user.get('user_id')).first()
  if not bcrypt_context.verify(user_verification.password, user_model.password_hash):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
  user_model.password_hash=bcrypt_context.hash(user_verification.new_password)
  db.commit()