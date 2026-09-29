"""Shared load → split → embed → Qdrant helpers.

Used by index.py (CLI) and by POST /index/.
"""

from __future__ import annotations

import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "sample_collection")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 400


def openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return key


def embedding_model() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=openai_api_key())


def load_and_split(pdf_path: Path) -> tuple[int, list]:
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents=docs)
    return len(docs), chunks


def qdrant_client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL)


def reset_collection() -> None:
    client = qdrant_client()
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)


def index_pdf(pdf_path: Path, replace: bool = False) -> dict:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if replace:
        reset_collection()

    pages, chunks = load_and_split(pdf_path)
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model(),
        collection_name=COLLECTION_NAME,
        url=QDRANT_URL,
    )
    return {
        "file": pdf_path.name,
        "path": str(pdf_path),
        "pages": pages,
        "chunks": len(chunks),
        "collection": COLLECTION_NAME,
        "replaced": replace,
    }


def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        embedding=embedding_model(),
        collection_name=COLLECTION_NAME,
        url=QDRANT_URL,
    )
