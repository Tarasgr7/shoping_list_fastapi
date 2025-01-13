from routers.shoping_list import get_current_user,get_db
from fastapi import status
from models import ShoppingLists
from .utils import *

app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=override_get_current_user

def test_read_all_shoping_list(test_shopping_list):
  response=client.get("/shopinglist/")
  assert response.status_code == status.HTTP_200_OK
  data=response.json()
  assert data[0]["id"] == test_shopping_list.id
  assert data[0]["name"] == test_shopping_list.name
  assert data[0]["description"] == test_shopping_list.description

def test_read_single_shoping_list(test_shopping_list):
  response=client.get("/shopinglist/Test Shopping List")
  assert response.status_code == status.HTTP_200_OK
  data=response.json()
  assert data["id"] == test_shopping_list.id
  assert data["name"] == test_shopping_list.name
  assert data["description"] == test_shopping_list.description

def test_read_single_shoping_list_not_found(test_shopping_list):
  response=client.get("/shopinglist/Not Found Shopping List")
  assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_shoping_list(test_shopping_list):
  new_list={"name": "Test Shopping List 2", "description": "Test Shopping List 2"}
  response=client.post("/shopinglist/", json=new_list)
  assert response.status_code == status.HTTP_201_CREATED
  db=TestingSessionLocal()
  model=db.query(ShoppingLists).filter(ShoppingLists.name == "Test Shopping List 2").first()
  assert model.name== new_list.get("name")
  assert model.description== new_list.get("description")


def test_update_shoping_list(test_shopping_list):
  new_list={"name": "Updated Shopping List", "description": "Updated Shopping List"}
  response=client.put("/shopinglist/Test Shopping List", json=new_list)
  assert response.status_code == status.HTTP_204_NO_CONTENT
  db=TestingSessionLocal()
  model=db.query(ShoppingLists).filter(ShoppingLists.name == "Updated Shopping List").first()
  assert model.name== new_list.get("name")
  assert model.description== new_list.get("description")

def test_update_shopping_list_not_found(test_shopping_list):
  new_list={"name": "Updated Shopping List", "description": "Updated Shopping List"}
  response=client.put("/shopinglist/Not Found Shopping List", json=new_list)
  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert response.json()== {'detail':"Shopping list not found"}

def test_delete_shoping_list(test_shopping_list):
  response=client.delete("/shopinglist/Test Shopping List")
  assert response.status_code == status.HTTP_204_NO_CONTENT
  db=TestingSessionLocal()
  model=db.query(ShoppingLists).filter(ShoppingLists.name == "Test Shopping List").first()
  assert model is None

def test_delete_shoping_list_not_found(test_shopping_list):
  response=client.delete("/shopinglist/Not Found Shopping List")
  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert response.json()== {'detail':"Shopping list not found"}
