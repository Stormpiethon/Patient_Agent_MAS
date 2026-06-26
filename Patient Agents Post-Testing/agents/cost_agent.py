"""
Cost Agent

Purpose:
    Calculate medication and procedure costs for a patient.

Responsibilities:
    - Resolve medication and procedure costs from the cost database
    - Build a structured cost breakdown
    - Generate a natural-language cost summary

Inputs:
    cost_context

Outputs:
    line_items
    total_cost
    cost_summary

Tools:
    analyze_cost_context
    llm_cost_summary
"""

"""
Example Input:

{
    "patient_id": "jd-001",
    "medications": [
        {
            "medication_id": "med-001",
            "name": "Metformin",
            "dose": "500mg",
            "cost_code": "RX1001"
        },
        {
            "medication_id": "med-002",
            "name": "Lisinopril",
            "dose": "10mg",
            "cost_code": "RX1002"
        }
    ],
    "procedures": [
        {
            "procedure_id": "proc-001",
            "name": "CBC Panel",
            "cost_code": "PROC2001"
        },
        {
            "procedure_id": "proc-002",
            "name": "Chest X-Ray",
            "cost_code": "PROC2002"
        }
    ]
}

Example Output:

{
    "agent": "cost_agent",
    "patient_id": "jd-001",
    "line_items": [
        {
            "type": "medication",
            "name": "Metformin",
            "dose": "500mg",
            "cost_code": "RX1001",
            "unit_cost": 15.0,
            "cost_period": "monthly",
            "status": "found"
        }
    ],
    "total_cost": 390.0,
    "cost_summary": "..."
}
"""

"""
Workflow:

Manager Agent
    →
Records Agent
    →
cost_context
    →
Cost Agent

Tool 1:
    analyze_cost_context()

Tool 2:
    llm_cost_summary()

Output:
    line_items
    total_cost
    cost_summary
    →
Manager Agent
"""

from tools.cost_tools import analyze_cost_context
from tools.llm_tools import llm_cost_analysis


def run_cost_agent(cost_context):

    line_items = analyze_cost_context(cost_context)

    total_cost = sum(
        item["unit_cost"]
        for item in line_items
        if item["unit_cost"] is not None
    )

    cost_summary = llm_cost_analysis(
        medications=cost_context.get("medications", []),
        procedures=cost_context.get("procedures", []),
        total_cost=total_cost
    )

    return {
        "agent": "cost_agent",

        "patient": {
            "patient_id": cost_context["patient_id"],
            "name": cost_context["name"],
            "age": cost_context["age"],
            "gender": cost_context["gender"]
        },

        "analysis": {
            "line_items": line_items,
            "total_cost": total_cost,
            "summary": cost_summary["cost_summary"]
        },

        "metadata": {
            "prompt_tokens": cost_summary["prompt_tokens"],
            "completion_tokens": cost_summary["completion_tokens"],
            "total_tokens": cost_summary["total_tokens"]
        }
    }
