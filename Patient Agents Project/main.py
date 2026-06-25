from agents.records_agent import get_labs_context, get_cost_context
from agents.labs_agent import run_labs_agent
from agents.cost_agent import run_cost_agent
from tools.records_tools import (
    get_patient_info,
    get_labs,
    get_medications,
    get_procedures,
    get_observations,
)

print("*** success on imports ***\n")

patient_id = "jd-001"

print("--- Records Agent Tools ---")
print(get_patient_info(patient_id))
print(get_labs(patient_id))
print(get_medications(patient_id))
print(get_procedures(patient_id))
print(get_observations(patient_id))

print("\n--- Labs Agent ---")
labs_result = run_labs_agent(get_labs_context(patient_id))
print(f"Patient: {labs_result['patient_id']}")
print(f"Findings: {len(labs_result['findings'])} lab results analyzed")

print("\n--- Cost Agent ---")
cost_result = run_cost_agent(get_cost_context(patient_id))
print(f"Patient: {cost_result['patient_id']}")
print(f"Line items: {len(cost_result['line_items'])}")
print(f"Total cost: ${cost_result['total_cost']:.2f}")
