import json

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.models import AnalysisResult, ClauseAnalysis, RiskFlag
from app.service.prompt import CONTRACT_ANALYSIS_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _strip_fences(raw_text: str) -> str:
    raw_text = raw_text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    return raw_text.strip()


async def analyze_contract(contract_id: str, text_content: str) -> AnalysisResult:
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text=text_content[:15000])
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You analyse Indian contracts and return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw_text = _strip_fences(completion.choices[0].message.content or "")
    analysis_data = json.loads(raw_text)

    key_clauses = [
        ClauseAnalysis(**clause) for clause in analysis_data.get("key_clauses", [])
    ]
    risk_flags = [
        RiskFlag(**risk) for risk in analysis_data.get("risk_flags", [])
    ]

    return AnalysisResult(
        contract_id=contract_id,
        summary=analysis_data.get("summary", ""),
        contract_type=analysis_data.get("contract_type", "Unknown"),
        key_clauses=key_clauses,
        risk_flags=risk_flags,
        overall_risk_level=analysis_data.get("overall_risk_level", "low"),
        recommendations=analysis_data.get("recommendations", []),
    )
