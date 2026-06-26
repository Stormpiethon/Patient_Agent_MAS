"""
Records Agent

Purpose:
    Retrieve patient information and create structured
    context objects for downstream agents.

Responsibilities:
    - Retrieve patient information
    - Build Labs Agent context
    - Build Cost Agent context
    - Provide structured outputs to downstream agents

Inputs:
    patient_id

Outputs:
    labs_context
    cost_context

Tools:
    get_patient_info
    get_labs
    get_observations
    get_medications
    get_procedures
"""

"""
Example Input:

{
    "patient_id": "jd-001"
}

Example Labs Context Output:

{
    "patient_id": "jd-001",
    "name": "John Doe",
    "age": 55,
    "gender": "Male",
    "previous_conditions": [],
    "labs": [...],
    "observations": [...],

    "encounter": {
        "chief_complaint": "",
        "nurse_notes": ""
    }
}

Example Cost Context Output:

{
    "patient_id": "jd-001",
    "name": "John Doe",
    "age": 55,
    "gender": "Male",
    "previous_conditions": [],
    "medications": [...],
    "procedures": [...]
}
"""

from tools.records_tools import (
    get_patient_info,
    get_labs,
    get_observations,
    get_medications,
    get_procedures
)

# Retrieve all needed context for the Labs Agent
def get_labs_context(
    patient_id,
    chief_complaint="",
    nurse_notes=""
):
    patient = get_patient_info(patient_id)

    return {
        "patient_id": patient_id,
        "name": patient["name"],
        "age": patient["age"],
        "gender": patient["gender"],
        "previous_conditions": patient["previous_conditions"],
        "labs": get_labs(patient_id),
        "observations": get_observations(patient_id),

        "encounter": {
            "chief_complaint": chief_complaint,
            "nurse_notes": nurse_notes
        }
    }

# Retrieve all needed context for Cost Agent
def get_cost_context(patient_id):
    patient = get_patient_info(patient_id)

    return {
        "patient_id": patient_id,
        "name": patient["name"],
        "age": patient["age"],
        "gender": patient["gender"],
        "previous_conditions": patient["previous_conditions"],
        "medications": get_medications(patient_id),
        "procedures": get_procedures(patient_id)
    }

# Retrieve all needed context for Risk Agent
def get_risk_context(
    patient_id,
    chief_complaint="",
    nurse_notes="",
    smoker=False,
    alcohol_use=False,
    drug_use=False
):
    patient = get_patient_info(patient_id)

    return {
        "patient_id": patient_id,
        "name": patient["name"],
        "age": patient["age"],
        "gender": patient["gender"],
        "previous_conditions": patient["previous_conditions"],
        "labs": get_labs(patient_id),
        "observations": get_observations(patient_id),

        "lifestyle": {
            "smoker": smoker,
            "alcohol_use": alcohol_use,
            "drug_use": drug_use
        },

        "encounter": {
            "chief_complaint": chief_complaint,
            "nurse_notes": nurse_notes
        }
    }