from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routes.analysis import router as analysis_router
from app.routes.contracts import router as contracts_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Vakeel Contracts API",
    description="AI-Powered Contract Analysis using OpenAI",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "app": "Vakeel Contracts API",
        "version": "1.0.0",
        "endpoints": {
            "POST /contracts/upload": "Upload a PDF or TXT contract for analysis",
            "GET /contracts/": "Retrieve a list of all uploaded contracts",
            "GET /contracts/{id}": "Retrieve details of a specific contract by ID",
            "POST /analysis/analyse/{contract_id}": "Analyze a contract using AI and return insights",
            "GET /analysis/{analysis_id}": "Retrieve the results of a specific analysis by ID",
            "GET /analysis/contract/{contract_id}": "Retrieve analyses for a specific contract",
        },
    }


app.include_router(contracts_router)
app.include_router(analysis_router)
