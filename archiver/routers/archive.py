from typing import Annotated
from fastapi import  Depends,APIRouter,status,HTTPException, Path
from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.orm import Session
from models import ShoppingLists, Items
from typing import List


router=APIRouter(
  prefix='/archive',
  tags=['archive']
)


def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()


db_dependency=Annotated[Session, Depends(get_db)]


class ArchiveRequest(BaseModel):
    list_id: int
    user_id: int
    name: str
    description: str
    items: List[dict]
    status: str

@router.get("/",status_code=status.HTTP_200_OK)
def get_all_archive(db:db_dependency):
   archived_lists=db.query(ShoppingLists).all()
   return archived_lists
@router.post("/",status_code=status.HTTP_201_CREATED)
def archive_list(request: ArchiveRequest, db: Session = Depends(get_db)):
    """
    Archives a shopping list.
    """
    existing_list = db.query(ShoppingLists).filter(ShoppingLists.id == request.list_id).first()
    if existing_list:
        raise HTTPException(status_code=400, detail="List is already archived.")

    new_list = ShoppingLists(
        id=request.list_id,
        user_id=request.user_id,
        name=request.name,
        description=request.description,
        status=request.status
    )
    db.add(new_list)
    db.commit()

    for item in request.items:
        new_item = Items(
            shoppinglist_id=request.list_id,
            name=item["name"],
            quantity=item["quantity"],
            status=item.get("status", "Uncompleted")
        )
        db.add(new_item)
    db.commit()

    return {"message": "List archived successfully.", "list_id": request.list_id}

@router.get("/{list_id}",status_code=status.HTTP_200_OK)
def get_archived_list(list_id: int, db: Session = Depends(get_db)):
    """
    Fetches details of an archived list.
    """
    archived_list = db.query(ShoppingLists).filter(ShoppingLists.id == list_id).first()
    if not archived_list:
        raise HTTPException(status_code=404, detail="Archived list not found.")

    items = db.query(Items).filter(Items.shoppinglist_id == list_id).all()
    return {
        "id": archived_list.id,
        "user_id": archived_list.user_id,
        "name": archived_list.name,
        "description": archived_list.description,
        "status": archived_list.status,
        "items": [
            {"id": item.id, "name": item.name, "quantity": item.quantity, "status": item.status}
            for item in items
        ]
    }

@router.delete("/{list_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_archived_list(list_id: int, db: Session = Depends(get_db)):
    """
    Deletes an archived list.
    """
    archived_list = db.query(ShoppingLists).filter(ShoppingLists.id == list_id).first()
    if not archived_list:
        raise HTTPException(status_code=404, detail="Archived list not found.")
    db.delete(archived_list)
    db.commit()
    return {"message": "Archived list deleted successfully.", "list_id": list_id}



