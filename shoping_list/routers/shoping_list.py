from fastapi import Depends,APIRouter,status,HTTPException, Path
from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.orm import Session
from models import ShoppingLists,Items
from utils.auth_utils import get_current_user
from typing import Annotated
from sqlalchemy import func
import requests
router=APIRouter(
  prefix='/shopinglist',
  tags=['shopinglist']
)

def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency=Annotated[Session, Depends(get_db)]
user_dependency=Annotated[dict, Depends(get_current_user)]


''' Endpoints for the Shopping lists'''
class ShoppingListsCreate(BaseModel):
  name: str
  description:str


@router.get('/',status_code=status.HTTP_200_OK)
async def get_shopping_lists(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  return db.query(ShoppingLists).filter(ShoppingLists.user_id==user.get('user_id')).all()


@router.get('/{list_name}',status_code=status.HTTP_200_OK)
async def get_shoping_list(user:user_dependency,db: db_dependency,list_name: str):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  shopping_list = db.query(ShoppingLists).filter(func.lower(ShoppingLists.name)==list_name.lower(),
                                                 ShoppingLists.user_id==user.get('user_id')).first()
  if shopping_list is not None:
    return shopping_list
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_shopping_list(user: user_dependency, db: db_dependency, shopping_list: ShoppingListsCreate):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  # new_shopping_list = ShoppingLists(**shopping_list.model_dump(), user_id=user.get('user_id'))
  new_shopping_list=ShoppingLists(user_id=user.get('user_id'), name=shopping_list.name, description=shopping_list.description)
  db.add(new_shopping_list)
  db.commit()

@router.put('/{list_name}',status_code=status.HTTP_204_NO_CONTENT)
async def update_shopping_list(user: user_dependency,db: db_dependency,
                               shopping_list_create: ShoppingListsCreate, list_name: str):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  shopping_list_model = db.query(ShoppingLists).filter(func.lower(ShoppingLists.name)==list_name.lower(),
                                                 ShoppingLists.user_id==user.get('user_id')).first()
  if shopping_list_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
  shopping_list_model.name=shopping_list_create.name
  shopping_list_model.description=shopping_list_create.description
  db.add(shopping_list_model)
  db.commit()

@router.delete('/{list_name}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(user: user_dependency, db: db_dependency, list_name: str):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  shopping_list_model = db.query(ShoppingLists).filter(func.lower(ShoppingLists.name)==list_name.lower(),
                                                 ShoppingLists.user_id==user.get('user_id')).first()
  if shopping_list_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
  db.delete(shopping_list_model)
  db.commit()

'''Endpoints for the Items'''

class ItemCreate(BaseModel):
  name: str
  quantity: int


@router.get('/{list_id}/item',status_code=status.HTTP_200_OK)
async def get_items_for_list(user:user_dependency, db:db_dependency,list_id: int):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  shopping_list = db.query(ShoppingLists).filter(ShoppingLists.id==list_id,
                                                 ShoppingLists.user_id==user.get('user_id')).first()
  if shopping_list is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
  return db.query(Items).filter(Items.shoppinglist_id==shopping_list.id).all()


@router.post('/{list_id}/item',status_code=status.HTTP_201_CREATED)
async def create_item(user: user_dependency, db: db_dependency, list_id: int, item: ItemCreate):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  shopping_list = db.query(ShoppingLists).filter(ShoppingLists.id==list_id,
                                                 ShoppingLists.user_id==user.get('user_id')).first()
  if shopping_list is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
  new_item = Items(shoppinglist_id=shopping_list.id, name=item.name, quantity=item.quantity)
  db.add(new_item)
  db.commit()


@router.put('/{list_name}/items/{item_name}',status_code=status.HTTP_204_NO_CONTENT)
async def update_item(user: user_dependency, db: db_dependency, list_name: str, item_name: str, item: ItemCreate):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  shopping_list = db.query(ShoppingLists).filter(func.lower(ShoppingLists.name)==list_name.lower(),
                                                 ShoppingLists.user_id==user.get('user_id')).first()
  if shopping_list is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
  item_model = db.query(Items).filter(func.lower(Items.name)==item_name.lower(), Items.shoppinglist_id==shopping_list.id).first()
  if item_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
  item_model.name=item.name
  item_model.quantity=item.quantity
  db.add(item_model)
  db.commit()

@router.delete('/{lisn_name}/items/{item_name}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(user: user_dependency, db: db_dependency, list_name: str, item_name: str):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  shopping_list = db.query(ShoppingLists).filter(func.lower(ShoppingLists.name)==list_name.lower(),
                                                 ShoppingLists.user_id==user.get('user_id')).first()
  if shopping_list is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
  item_model = db.query(Items).filter(func.lower(Items.name)==item_name.lower(), Items.shoppinglist_id==shopping_list.id).first()
  if item_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
  db.delete(item_model)
  db.commit()


ARCHIVE_SERVICE_URL = "http://0.0.0.0:8000/archive/"



@router.get("/archive")
def get_all_archive():
    """
    Returns all archived shopping lists.
    """
    try:
        response = requests.get(ARCHIVE_SERVICE_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=err.response.status_code, detail=err.response.text)

@router.post("/{list_id}/archive")
def archive_shopping_list(list_id: int, db: db_dependency):
    """
    Sends a shopping list to the archive service.
    """
    try:
        items_list = []
        shopping_list = db.query(ShoppingLists).filter_by(id=list_id).first()
        if not shopping_list:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        
        items = db.query(Items).filter_by(shoppinglist_id=list_id).all()
        
        # Перетворення списку елементів на словники
        for i in items:
            items_list.append({
                "name": i.name,
                "quantity": i.quantity,
                "status": i.status,
                "shoppinglist_id": i.shoppinglist_id
            })
        
        # Перетворення shopping_list на словник
        shopping_list_dict = {
            "list_id": shopping_list.id,
            "user_id": shopping_list.user_id,
            "name": shopping_list.name,
            "description": shopping_list.description,
            "status": shopping_list.status
        }

        # Формуємо payload для запиту
        response = requests.post(ARCHIVE_SERVICE_URL, json={
            **shopping_list_dict,
            "items": items_list
        })
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to archive list: {e}")

@router.get("/{list_id}/archive")
def get_archived_shopping_list(list_id: int):
    """
    Retrieves an archived shopping list from the archive service.
    """
    try:
        response = requests.get(f"{ARCHIVE_SERVICE_URL}{list_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve archived list: {e}")

@router.delete("/{list_id}/archive")
def delete_archived_shopping_list(list_id: int):
    """
    Deletes an archived shopping list from the archive service.
    """
    try:
        response = requests.delete(f"{ARCHIVE_SERVICE_URL}{list_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete archived list: {e}")
