from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

from app.rag import CHAT_MODEL, get_vector_store, openai_api_key

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question to ask against the indexed PDF")


@router.post("/")
async def query(body: QueryRequest):
    question = body.question.strip()

    try:
        openai_api_key()
        vector_db = get_vector_store()
        search_results = vector_db.similarity_search(query=question)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Could not search Qdrant. Start it with `docker compose up -d` "
                "and index a PDF via POST /index/ first. "
                f"({exc})"
            ),
        ) from exc

    if not search_results:
        return {
            "question": question,
            "answer": "I don't know.",
            "sources": [],
        }

    context = " ".join(
        [
            f"[Page {result.metadata.get('page', 'unknown')}] {result.page_content}"
            for result in search_results
        ]
    )

    system_prompt = f"""
You are a helpful assistant that answers questions based on the provided context.
If the context does not contain the answer, respond with \"I don't know.\"

Also include the page number of the context in your answer if applicable.

Context:
{context}
    \"\"\".strip()

    response = OpenAI(api_key=openai_api_key()).chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    sources = [
        {
            "page": result.metadata.get("page"),
            "source": result.metadata.get("source"),
            "preview": result.page_content[:220],
        }
        for result in search_results
    ]

    return {
        "question": question,
        "answer": response.choices[0].message.content,
        "sources": sources,
    }
