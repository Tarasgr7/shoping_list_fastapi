from fastapi import FastAPI, HTTPException, Depends
from kafka import KafkaConsumer
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
import json
from threading import Thread

# Налаштування FastAPI
app = FastAPI()

# Конфігурація Kafka
KAFKA_TOPIC = "shopping_list_completed"
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]

# Ініціалізація Kafka-споживача
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

# Налаштування бази даних
DATABASE_URL = "sqlite:///./archive.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Опис таблиць бази даних
class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    items = relationship("ShoppingListItem", back_populates="shopping_list")

class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"
    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    shopping_list = relationship("ShoppingList", back_populates="items")

# Створення таблиць
Base.metadata.create_all(bind=engine)

# Залежність для отримання сесії бази даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функція для обробки повідомлень із Kafka
def save_shopping_list(data):
    db = SessionLocal()
    try:
        shopping_list = ShoppingList(
            user_id=data["user_id"],
            name=data["list_name"],
            description=data.get("description"),
        )
        db.add(shopping_list)
        db.commit()
        db.refresh(shopping_list)

        for item in data["items"]:
            db.add(
                ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    name=item["name"],
                    quantity=item["quantity"],
                )
            )
        db.commit()
        print(f"Archived shopping list: {shopping_list.name}")
    except Exception as e:
        db.rollback()
        print(f"Error saving shopping list: {e}")
    finally:
        db.close()

# Фоновий потік для споживання Kafka-повідомлень
def consume_kafka_messages():
    for message in consumer:
        save_shopping_list(message.value)

# Запуск потоку споживача при старті програми
@app.on_event("startup")
def start_kafka_consumer():
    thread = Thread(target=consume_kafka_messages, daemon=True)
    thread.start()


@app.get("/archived/shopping-lists")
def get_all_archived_lists(db: Session = Depends(get_db)):
    lists = db.query(ShoppingList).all()
    if not lists:
        raise HTTPException(status_code=404, detail="No archived shopping lists found")
    result = []
    for shopping_list in lists:
        items = [
            {"name": item.name, "quantity": item.quantity}
            for item in shopping_list.items
        ]
        result.append(
            {
                "id": shopping_list.id,
                "user_id": shopping_list.user_id,
                "name": shopping_list.name,
                "description": shopping_list.description,
                "items": items,
            }
        )
    return result


# @app.get("/get-archived-shopping-lists")
# def get_archived_shopping_lists():
#     """
#     Отримує архівовані списки покупок з мікросервісу.
#     """
#     # Логіка для отримання архівованих списків з бази даних або іншого джерела
#     archived_lists = [
#         {"id": 1, "name": "Groceries", "items": [{"name": "Milk", "quantity": 2}, {"name": "Bread", "quantity": 1}]},
#         {"id": 2, "name": "Party Supplies", "items": [{"name": "Chips", "quantity": 3}, {"name": "Soda", "quantity": 5}]}
#     ]
#     if not archived_lists:
#         raise HTTPException(status_code=404, detail="No archived shopping lists found")
    
#     return archived_lists