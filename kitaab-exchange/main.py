from fastapi import FastAPI
from database import create_tables
from routes import books, users


app = FastAPI(
    title="Kitab Exchange API",
    description="A simple API for exchanging used books",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    create_tables()


app.include_router(users.router)
app.include_router(books.router)


@app.get("/")
def home():
    return {"message": "Welcome to the Kitab Exchange API"}
