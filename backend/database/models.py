from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .db import Base

class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    abstract = Column(Text)
    field = Column(String(128))
    keywords = Column(String(512))  
    created_at = Column(DateTime, server_default=func.now())

class Trend(Base):
    __tablename__ = "trends"
    id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String(64), unique=True, index=True)
    title = Column(String(512))
    summary = Column(Text)
    field = Column(String(128))
    published_at = Column(String(64))


