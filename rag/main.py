from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.routes.index import router as index_router
from app.routes.query import router as query_router

app = FastAPI(
    title="RAG API",
    description="Upload a PDF, then ask questions against the chunks stored in Qdrant.",
    version="0.2.0",
)

app.include_router(index_router)
app.include_router(query_router)


@app.get("/")
def root():
    return {
        "name": "RAG API",
        "docs": "/docs",
        "index": "POST /index/  multipart file=your.pdf  replace=false",
        "query": "POST /query/  {\"question\": \"What is RAG?\"}",
    }
