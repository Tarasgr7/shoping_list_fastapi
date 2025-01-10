from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth,users,shoping_list

app=FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
  return {"message": "Hello World"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(shoping_list.router)