from confluent_kafka import Producer
import json

def create_kafka_producer():
    conf = {
        'bootstrap.servers': 'localhost:9092',  # Адреса Kafka сервера
        'client.id': 'shopping-list-client'
    }
    producer = Producer(conf)
    return producer

def send_message(producer, topic, message):
    producer.produce(topic, message.encode('utf-8'))
    producer.flush()  # Переконайтеся, що всі повідомлення відправлені
