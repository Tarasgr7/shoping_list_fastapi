from fastapi import FastAPI
from database import Base, engine
from routers import archive
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(archive.router)

