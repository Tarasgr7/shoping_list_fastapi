from fastapi import FastAPI, HTTPException, Depends
from kafka import KafkaConsumer
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
import json




app=FastAPI()

DATABASE_URL = "sqlite:///./archive.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)