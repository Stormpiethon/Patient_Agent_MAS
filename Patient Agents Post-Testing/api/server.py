"""
FastAPI server for the Clinical Decision Support intake UI.
"""

from pathlib import Path
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from agents.records_agent import get_labs_context
from main import route_request
from tools.records_tools import get_patient_info

app = FastAPI(title="Clinical Decision Support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    patient_id: str = Field(..., min_length=1)
    chief_complaint: str = ""
    nurse_notes: str = ""
    smoker: bool = False
    alcohol_use: bool = False
    drug_use: bool = False
    laboratory_review: bool = False
    risk_assessment: bool = False
    cost_estimate: bool = False


def _build_requested_agents(payload: AnalysisRequest) -> list[str]:
    requested = []
    if payload.laboratory_review:
        requested.append("labs")
    if payload.risk_assessment:
        requested.append("risk")
    if payload.cost_estimate:
        requested.append("cost")
    return requested


def _format_response(payload: AnalysisRequest, result: dict, records_context: dict) -> dict:
    outputs = result.get("agent_outputs", {})
    labs = outputs.get("labs")
    risk = outputs.get("risk")
    cost = outputs.get("cost")

    patient_source = None
    for source in (labs, risk, cost):
        if source and source.get("patient"):
            patient_source = source["patient"]
            break

    patient = {
        "patient_id": payload.patient_id,
        "name": patient_source.get("name") if patient_source else records_context.get("name"),
        "age": patient_source.get("age") if patient_source else records_context.get("age"),
        "gender": patient_source.get("gender") if patient_source else records_context.get("gender"),
        "previous_conditions": (
            patient_source.get("previous_conditions")
            if patient_source and patient_source.get("previous_conditions") is not None
            else records_context.get("previous_conditions", [])
        ),
    }

    response = {
        "patient": patient,
        "chief_complaint": payload.chief_complaint,
        "nurse_notes": payload.nurse_notes,
        "lifestyle": {
            "smoker": payload.smoker,
            "alcohol_use": payload.alcohol_use,
            "drug_use": payload.drug_use,
        },
        "requested_analyses": {
            "laboratory_review": payload.laboratory_review,
            "risk_assessment": payload.risk_assessment,
            "cost_estimate": payload.cost_estimate,
        },
        "recommended_discussion": result.get("final_output", ""),
    }

    if payload.laboratory_review and labs:
        analysis = labs.get("analysis", {})
        response["laboratory_findings"] = analysis.get("findings", [])
        concerns = analysis.get("health_concerns", [])
        if isinstance(concerns, str):
            response["potential_health_concerns"] = [concerns] if concerns else []
        else:
            response["potential_health_concerns"] = concerns

    if payload.risk_assessment and risk:
        analysis = risk.get("analysis", {})
        response["risk_assessment"] = {
            "risk_score": analysis.get("risk_score"),
            "risk_level": analysis.get("risk_level"),
            "risk_factors": analysis.get("risk_factors", []),
            "summary": analysis.get("summary", ""),
        }

    if payload.cost_estimate and cost:
        analysis = cost.get("analysis", {})
        response["estimated_costs"] = {
            "line_items": analysis.get("line_items", []),
            "total_cost": analysis.get("total_cost"),
            "summary": analysis.get("summary", ""),
        }

    return response


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/generate")
def generate_summary(payload: AnalysisRequest):
    requested = _build_requested_agents(payload)
    if not requested:
        raise HTTPException(
            status_code=400,
            detail="Select at least one requested analysis.",
        )

    patient_info = get_patient_info(payload.patient_id)
    if not patient_info:
        raise HTTPException(
            status_code=404,
            detail=f"Patient record not found: {payload.patient_id}",
        )

    try:
        records_context = get_labs_context(
            payload.patient_id,
            payload.chief_complaint,
            payload.nurse_notes,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    request = {
        "patient_id": payload.patient_id,
        "requested_agents": requested,
        "chief_complaint": payload.chief_complaint,
        "nurse_notes": payload.nurse_notes,
        "smoker": payload.smoker,
        "alcohol_use": payload.alcohol_use,
        "drug_use": payload.drug_use,
    }

    try:
        result = route_request(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return _format_response(payload, result, records_context)
