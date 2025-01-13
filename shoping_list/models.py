from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Users(Base):
  __tablename__ = "users"
  id=Column(Integer,primary_key=True,index=True)
  username=Column(String,index=True,unique=True)
  email=Column(String,unique=True)
  password_hash=Column(String)
  

from sqlalchemy.orm import relationship

class ShoppingLists(Base):
    __tablename__ = "shoppinglists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    items = relationship(
        "Items",
        back_populates="shoppinglist",
        passive_deletes=True  # Підтримка ondelete="CASCADE"
    )

class Items(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    shoppinglist_id = Column(Integer, ForeignKey("shoppinglists.id", ondelete="CASCADE"))
    name = Column(String)
    quantity = Column(Integer)
    shoppinglist = relationship("ShoppingLists", back_populates="items")



