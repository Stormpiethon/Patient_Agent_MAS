"""
Risk Assessment Agent

Purpose:
    Analyze patient risk factors using structured
    patient data and laboratory findings.

Inputs:
    risk_context

Outputs:
    risk_assessment

Tools:
    extract_risk_factors
    calculate_risk_score
    llm_risk_summary
"""

"""
Example Input:

{
  "patient_id": "jd-006",
  "age": 45,
  "gender": "Female",

  "conditions": [
    "Type 2 Diabetes",
    "Hypertension"
  ],

  "labs": [
    {
      "lab_id": "lab-001",
      "name": "Glucose",
      "value": 287,
      "unit": "mg/dL",
      "reference_low": 70,
      "reference_high": 99
    }
  ],

  "observations": [
    {
      "date": "2026-06-14",
      "note": "Patient reports fatigue and excessive thirst."
    }
  ],

  "survey_data": {
    "smoker": true,
    "alcohol_use": false,
    "drug_use": false,
    "previous_heart_attack": true
  }
}

Example Output:

{
  "agent": "risk_agent",
  "patient_id": "jd-006",
  "risk_score": 14,
  "risk_factors": [
    "High Glucose",
    "Type 2 Diabetes",
    "Hypertension",
    "Smoking",
    "Previous Heart Attack"
  ],
  "summary": "Patient presents several cardiovascular and metabolic risk factors..."
}
"""

from tools.risk_tools import calculate_risk
from tools.llm_tools import llm_risk_summary


def run_risk_agent(risk_context):

    risk_result = calculate_risk(risk_context)

    summary = llm_risk_summary(
        risk_context=risk_context,
        risk_score=risk_result["risk_score"],
        risk_level=risk_result["risk_level"],
        risk_factors=risk_result["risk_factors"]
    )

    return {
        "agent": "risk_agent",

        "patient": {
            "patient_id": risk_context["patient_id"],
            "name": risk_context["name"],
            "age": risk_context["age"],
            "gender": risk_context["gender"]
        },

        "analysis": {
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "risk_factors": risk_result["risk_factors"],
            "summary": summary["risk_summary"]
        },

        "metadata": {
            "prompt_tokens": summary["prompt_tokens"],
            "completion_tokens": summary["completion_tokens"],
            "total_tokens": summary["total_tokens"]
        }
    }