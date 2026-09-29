from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.rag import DATA_DIR, index_pdf

router = APIRouter(prefix="/index", tags=["index"])


def _safe_pdf_name(filename: str | None) -> str:
    name = Path(filename or "").name
    if not name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are accepted.")
    if name in {".", ".."} or not name.replace(".pdf", "").replace(".PDF", ""):
        raise HTTPException(status_code=400, detail="Invalid file name.")
    return name


@router.post("/")
async def upload_and_index(
    file: UploadFile = File(..., description="PDF to chunk and store in Qdrant"),
    replace: bool = Form(
        False,
        description="If true, delete sample_collection first. If false, add to it.",
    ),
):
    filename = _safe_pdf_name(file.filename)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_DIR / filename

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    dest.write_bytes(payload)

    try:
        result = index_pdf(dest, replace=replace)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Could not index into Qdrant. Is Docker running? "
                f"Try `docker compose up -d`. ({exc})"
            ),
        ) from exc

    result["replace"] = replace
    return result
