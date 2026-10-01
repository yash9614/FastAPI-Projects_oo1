import os
import uuid

from bson import ObjectId
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIR
from app.database import contracts_collection
from app.models import Contact
from app.service.document_parser import extract_text

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """Upload a PDF or TXT contract for analysis."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the maximum limit of 10 MB",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(content)

    parsed = extract_text(file_path)
    contract_data = Contact(
        filename=unique_name,
        original_name=file.filename or unique_name,
        text_content=parsed["text"],
        page_count=int(parsed["page_count"]),
        word_count=int(parsed["word_count"]),
    )

    doc = contract_data.model_dump(exclude={"id"})
    result = contracts_collection.insert_one(doc)
    contract_data.id = str(result.inserted_id)

    return {
        "message": "File uploaded and processed successfully",
        "contract": contract_data.model_dump(),
        "id": contract_data.id,
    }


@router.get("/")
async def list_contracts():
    """List all uploaded contracts. Text body is omitted."""
    contracts = []
    for doc in contracts_collection.find({}, {"text_content": 0}):
        contract = Contact(
            filename=doc["filename"],
            original_name=doc["original_name"],
            upload_date=doc.get("upload_date", ""),
            page_count=int(doc.get("page_count", 0)),
            word_count=int(doc.get("word_count", 0)),
            status=doc.get("status", "uploaded"),
        )
        contract.id = str(doc["_id"])
        contracts.append(contract.model_dump())
    return {"contracts": contracts}


@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """Retrieve a specific contract by its ID."""
    try:
        doc = contracts_collection.find_one({"_id": ObjectId(contract_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid contract id")
    if not doc:
        raise HTTPException(status_code=404, detail="Contract not found")

    contract = Contact(
        filename=doc["filename"],
        original_name=doc["original_name"],
        upload_date=doc.get("upload_date", ""),
        text_content=doc.get("text_content", ""),
        page_count=int(doc.get("page_count", 0)),
        word_count=int(doc.get("word_count", 0)),
        status=doc.get("status", "uploaded"),
    )
    contract.id = str(doc["_id"])
    return {"contract": contract.model_dump()}
