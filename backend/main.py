from fastapi import FastAPI, UploadFile, File
from routers import papers, classify, trends
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from database.db import engine
from database import models


load_dotenv()

app = FastAPI(
    title="Paper2Video API",
    description="Upload research papers and generate summarized videos using Gemini API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router, prefix="/papers", tags=["Papers"])
app.include_router(classify.router, prefix="/classify", tags=["Classification"])
app.include_router(trends.router, prefix="/trends", tags=["Trends"])

@app.get("/")
def root():
    return {"message": "Welcome to Paper2Video API "}

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)

