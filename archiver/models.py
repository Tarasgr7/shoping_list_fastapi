from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


from sqlalchemy.orm import relationship

class ShoppingLists(Base):
    __tablename__ = "shoppinglists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    user_id = Column(Integer)
    status=Column(String,default="Uncompleted")
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
    status=Column(String,default="Uncompleted")