from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_tables
from models import Order, StatusLog  # noqa: F401 — register tables with SQLModel
from routes.orders import router as orders_router
from routes.stats import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan started")
    create_tables()
    print("Database tables created")
    yield
    print("Shutting down the app")


app = FastAPI(
    title="Dabbawala Delivery API",
    description="API for managing dabbawala deliveries and tracking order statuses.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(orders_router)
app.include_router(stats_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Dabbawala tracking API",
        "status_flow": ["preparing", "picked_up", "in_transit", "delivered"],
    }


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
