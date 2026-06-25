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
    "age": 55,
    "gender": "Male",
    "labs": [...],
    "observations": [...]
}

Example Cost Context Output:

{
    "patient_id": "jd-001",
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
def get_labs_context(patient_id):
    patient = get_patient_info(patient_id)

    return {
        "patient_id": patient_id,
        "age": patient["age"],
        "gender": patient["gender"],
        "labs": get_labs(patient_id),
        "observations": get_observations(patient_id)
    }

# Retrieve all needed context for Cost Agent
def get_cost_context(patient_id):
    return {
        "patient_id": patient_id,
        "medications": get_medications(patient_id),
        "procedures": get_procedures(patient_id)
    }