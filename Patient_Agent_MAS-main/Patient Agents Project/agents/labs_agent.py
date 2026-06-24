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


def run_labs_agent(labs_context):

    findings = analyze_labs_context(labs_context)

    abnormal_findings = [
        finding
        for finding in findings
        if finding["status"] != "normal"
    ]

    concerns = "No abnormal laboratory findings detected."

    if abnormal_findings:

        concerns = llm_lab_analysis(
            findings=findings,
            observations=labs_context.get(
                "observations",
                []
            ),
            age=labs_context.get("age"),
            gender=labs_context.get("gender")
        )

    return {
        "agent": "labs_agent",
        "patient_id": labs_context["patient_id"],
        "findings": findings,
        "potential_health_concerns": concerns
    }