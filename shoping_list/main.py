from fastapi import FastAPI,Request
from models import Base
from database import engine
from routers import auth,users,shoping_list
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
load_dotenv()


app=FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "default_secret_key"))


Base.metadata.create_all(bind=engine)



app.include_router(auth.router)
app.include_router(users.router)
app.include_router(shoping_list.router)

