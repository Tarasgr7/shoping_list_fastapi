from fastapi.testclient import TestClient

from sqlalchemy import create_engine,text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

import pytest

from database import Base
from main import app
from models import Users,ShoppingLists,Items
from utils.auth_utils import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"


engine = create_engine(
  SQLALCHEMY_DATABASE_URL,
  connect_args={"check_same_thread": False},
  poolclass=StaticPool,
  )
TestingSessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
  db=TestingSessionLocal()
  try:
    yield db
  finally:
    db.close()

def override_get_current_user():
  return {"user_id": 1, "username": "random"}

client=TestClient(app)

@pytest.fixture
def test_user():
  user=Users(username="random",email="test_user@example.com", password_hash=bcrypt_context.hash("testpassword"))
  db=TestingSessionLocal()
  db.add(user)
  db.commit()
  yield user
  with engine.connect() as connection:
    connection.execute(text("DELETE FROM users;"))
    connection.commit()
@pytest.fixture
def test_shopping_list():
  shopping_list=ShoppingLists(
    name="Test Shopping List",
    user_id=1,
    description="Test Shopping List",
  )
  db=TestingSessionLocal()
  db.add(shopping_list)
  db.commit()
  yield shopping_list
  with engine.connect() as connection:
    connection.execute(text("DELETE FROM shoppinglists;"))
    connection.commit()
@pytest.fixture
def test_item():
  list_item=Items(
    shoppinglist_id=1,
    name="Test Item",
    quantity=1
  )
  db=TestingSessionLocal()
  db.add(list_item)
  db.commit()
  yield list_item
  with engine.connect() as connection:
    connection.execute(text("DELETE FROM items;"))
    connection.commit()
