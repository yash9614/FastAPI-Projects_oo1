from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.config import OPENAI_API_KEY
from app.database import analysis_collection, contracts_collection
from app.service.gemini_analyse import analyze_contract

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _convert_obj(obj):
    if isinstance(obj, list):
        return [_convert_obj(v) for v in obj]
    if isinstance(obj, dict):
        new = {}
        for key, value in obj.items():
            if key == "_id":
                new["id"] = str(value)
            else:
                new[key] = _convert_obj(value)
        return new
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj


@router.post("/analyse/{contract_id}")
async def analyse_contract(contract_id: str):
    """Analyze a contract using OpenAI and store the insights."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured")

    try:
        oid = ObjectId(contract_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid contract id")

    contract = contracts_collection.find_one({"_id": oid})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if not contract.get("text_content"):
        raise HTTPException(status_code=400, detail="Contract has no text content to analyze")

    contracts_collection.update_one(
        {"_id": oid}, {"$set": {"status": "analyzing"}}
    )

    try:
        result = await analyze_contract(contract_id, contract["text_content"])
    except Exception as exc:
        contracts_collection.update_one(
            {"_id": oid}, {"$set": {"status": "error"}}
        )
        raise HTTPException(status_code=502, detail=f"Analysis failed: {exc}") from exc

    doc = result.model_dump(exclude={"id"})
    insert_result = analysis_collection.insert_one(doc)
    result.id = str(insert_result.inserted_id)

    contracts_collection.update_one(
        {"_id": oid}, {"$set": {"status": "analyzed"}}
    )

    return {
        "message": "Contract analyzed successfully",
        "analysis": result.model_dump(),
        "id": result.id,
    }


@router.get("/contract/{contract_id}")
async def get_analyses_for_contract(contract_id: str):
    """Get all analyses for a specific contract."""
    analyses = []
    for doc in analysis_collection.find({"contract_id": contract_id}):
        analyses.append(_convert_obj(doc))
    return {"analyses": analyses, "total": len(analyses)}


@router.get("/")
def list_analyses():
    """List all analyses performed."""
    analyses = [_convert_obj(doc) for doc in analysis_collection.find({})]
    return {"analyses": analyses}


@router.get("/{analysis_id}")
def get_analysis(analysis_id: str):
    """Retrieve the results of a specific analysis by ID."""
    try:
        analysis = analysis_collection.find_one({"_id": ObjectId(analysis_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid analysis id")
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"analysis": _convert_obj(analysis)}
