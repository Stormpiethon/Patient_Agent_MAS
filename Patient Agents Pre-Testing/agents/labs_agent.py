"""
Labs Agent

Purpose:
    Analyze laboratory results and observations.

Responsibilities:
    - Review laboratory findings
    - Identify abnormal values
    - Generate structured findings
    - Request AI-generated health concerns when abnormalities exist

Inputs:
    labs_context

Outputs:
    findings
    potential_health_concerns

Tools:
    analyze_labs_context
    llm_lab_analysis
"""

"""
Example Input:

{
    "patient_id": "jd-006",
    "age": 45,
    "gender": "Female",
    "previous_conditions": [],

    "labs": [
        {
            "lab_id": "lab-001",
            "name": "Glucose",
            "value": 287,
            "unit": "mg/dL",
            "reference_low": 70,
            "reference_high": 99
        },
        {
            "lab_id": "lab-002",
            "name": "WBC",
            "value": 18.9,
            "unit": "K/uL",
            "reference_low": 4.0,
            "reference_high": 11.0
        }
    ],

    "observations": [
        {
            "date": "2026-06-14",
            "note": "Patient reports excessive thirst and frequent urination."
        },
        {
            "date": "2026-06-14",
            "note": "Patient reports fatigue and fever."
        }
    ]
}

Example Output:

{
    "agent": "labs_agent",

    "patient_id": "jd-006",

    "findings": [
        {
            "lab_id": "lab-001",
            "lab": "Glucose",
            "value": 287,
            "unit": "mg/dL",
            "reference_low": 70,
            "reference_high": 99,
            "status": "high"
        },
        {
            "lab_id": "lab-002",
            "lab": "WBC",
            "value": 18.9,
            "unit": "K/uL",
            "reference_low": 4.0,
            "reference_high": 11.0,
            "status": "high"
        }
    ],

    "potential_health_concerns": [
        "Possible uncontrolled diabetes",
        "Possible infection",
        "Possible metabolic dysfunction"
    ]
}
"""

"""
Workflow:

Manager Agent
    →
Records Agent
    →
labs_context
    →
Labs Agent

Tool 1:
    analyze_labs_context()

Tool 2:
    llm_lab_analysis()

Output:
    findings
    potential_health_concerns
    →
Manager Agent
"""

from tools.lab_tools import analyze_labs_context
from tools.llm_tools import llm_lab_analysis


def run_labs_agent(records_context):

    labs = records_context.get("labs", [])
    observations = records_context.get("observations", [])
    encounter = records_context.get("encounter", {})

    findings = []

    for lab in labs:

        status = analyze_labs_context(
            lab["value"],
            lab["reference_low"],
            lab["reference_high"]
        )

        findings.append({
            "lab_id": lab["lab_id"],
            "name": lab["name"],
            "value": lab["value"],
            "unit": lab["unit"],
            "reference_low": lab["reference_low"],
            "reference_high": lab["reference_high"],
            "status": status
        })

    abnormal_exists = any(f["status"] != "normal" for f in findings)

    if abnormal_exists:

        llm_result = llm_lab_analysis(
            findings=findings,
            age=records_context["age"],
            gender=records_context["gender"],
            previous_conditions=records_context["previous_conditions"],
            observations=observations,
            encounter=encounter
        )

    else:
        llm_result = {
            "health_concerns": "No abnormal laboratory findings identified.",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    return {
        "agent": "labs_agent",

        "patient": {
            "patient_id": records_context["patient_id"],
            "name": records_context["name"],
            "age": records_context["age"],
            "gender": records_context["gender"],
            "previous_conditions": records_context["previous_conditions"]
        },

        "analysis": {
            "findings": findings,
            "health_concerns": llm_result["health_concerns"]
        },

        "metadata": {
            "prompt_tokens": llm_result["prompt_tokens"],
            "completion_tokens": llm_result["completion_tokens"],
            "total_tokens": llm_result["total_tokens"]
        }
    }