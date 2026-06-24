"""
Records Agent

Purpose:
    Retrieve patient information and create structured
    context objects for downstream agents.

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

from tools.patient_data import *

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