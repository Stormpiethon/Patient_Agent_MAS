from agents.tools.lab_tools import (
    detect_abnormal
)
from agents.tools.llm_tools import llm_analysis     

def run_labs_agent(records_output):
    findings = []

    for lab in records_output.get("labs", []):
        status = detect_abnormal(
            lab["value"],
            lab["reference_low"],
            lab["reference_high"]
        )

        findings.append({
            "lab": lab["name"],
            "status": status,
            "value": lab["value"],
            "unit": lab["unit"],
            "reference_low": lab["reference_low"],
            "reference_high": lab["reference_high"],
            "related_observations": context_search(
                lab["name"],
                records_output.get("observations", [])
            )
        })

    concerns = llm_analysis(findings)                  

    return {
        "agent": "labs_agent",
        "patient_id": records_output["patient_id"],
        "findings": findings,
        "potential_health_concerns": concerns            
    }