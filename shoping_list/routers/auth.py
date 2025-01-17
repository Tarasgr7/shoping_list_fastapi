from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, APIRouter,Request
from jose import JWTError, jwt
from fastapi import status
from models import Users
from pydantic import BaseModel
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from utils.auth_utils import *
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests
import httpx

from fastapi.templating import Jinja2Templates


load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")



router= APIRouter(
  prefix='/auth',
  tags=['auth']
)

templates = Jinja2Templates(directory="templates")

class LoginData(BaseModel):
    username: str
    password: str


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

@router.get('/login',status_code=status.HTTP_200_OK)
def my_template(request: Request):
   return templates.TemplateResponse(
        name="login.html",
        context={"request": request}
    )


@router.post('/', status_code=status.HTTP_201_CREATED )
async def create_user(db: db_dependency, create_user_request:CreateUserRequest):
  existing_user_by_username = db.query(Users).filter(Users.username == create_user_request.username).first()
  existing_user_by_email = db.query(Users).filter(Users.email == create_user_request.email).first()
  if existing_user_by_username:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
  if existing_user_by_email:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
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
  return {"user_id": create_user_model.id, "username": create_user_model.username}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: LoginData,
    db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        print("Помилка 1")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(user.username, user.id, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}




@router.get("/auth")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid email profile"

    return RedirectResponse(url=google_auth_url)

@router.get("/callback",status_code=status.HTTP_201_CREATED)
async def auth_callback(code: str, request: Request,db: db_dependency):
    token_request_uri = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': request.url_for('auth_callback'),
        'grant_type': 'authorization_code',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_request_uri, data=data)
        response.raise_for_status()
        token_response = response.json()
    id_token_value = token_response.get('id_token')
    if not id_token_value:
        raise HTTPException(status_code=400, detail="Missing id_token in response.")
    try:
        id_info = id_token.verify_oauth2_token(id_token_value, requests.Request(), GOOGLE_CLIENT_ID)
        name = id_info.get('name')
        request.session['user_name'] = name
        email=id_info.get('email')




        existing_user = db.query(Users).filter(Users.email == email).first()
        if existing_user:
            print("User already exists in the database.")
            return RedirectResponse(url=request.url_for('welcome'))
        new_user = Users(
            username=email,
            email=email,
            password_hash=None  
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  
        print("User created successfully.")
        return RedirectResponse(url=request.url_for('welcome'))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid id_token: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    



@router.get("/welcome")
async def welcome(request: Request):
    """
    :param request: The incoming HTTP request containing session data.
    :return: A TemplateResponse object that renders the welcome page with the user's name or 'Guest' if not found.
    """
    name = request.session.get('user_name', 'Guest')
    context = {"request": request, "name": name}
    return templates.TemplateResponse("welcome.html", context)