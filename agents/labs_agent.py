from tools.lab_tools import analyze_labs_context
from tools.llm_tools import llm_lab_analysis


async def run_labs_agent(records_context):
    labs = records_context.get("labs", [])
    observations = records_context.get("observations", [])
    encounter = records_context.get("encounter", {})

    findings = []

    for lab in labs:
        status = analyze_labs_context(
            lab["value"],
            lab["reference_low"],
            lab["reference_high"],
        )

        findings.append({
            "lab_id": lab["lab_id"],
            "name": lab["name"],
            "value": lab["value"],
            "unit": lab["unit"],
            "reference_low": lab["reference_low"],
            "reference_high": lab["reference_high"],
            "status": status,
        })

    abnormal_exists = any(f["status"] != "normal" for f in findings)

    if abnormal_exists:
        llm_result = await llm_lab_analysis(
            findings=findings,
            age=records_context["age"],
            gender=records_context["gender"],
            previous_conditions=records_context["previous_conditions"],
            observations=observations,
            encounter=encounter,
        )
    else:
        llm_result = {
            "health_concerns": "No abnormal laboratory findings identified.",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    return {
        "agent": "labs_agent",
        "patient": {
            "patient_id": records_context["patient_id"],
            "name": records_context["name"],
            "age": records_context["age"],
            "gender": records_context["gender"],
            "previous_conditions": records_context["previous_conditions"],
        },
        "analysis": {
            "findings": findings,
            "health_concerns": llm_result["health_concerns"],
        },
        "metadata": {
            "prompt_tokens": llm_result["prompt_tokens"],
            "completion_tokens": llm_result["completion_tokens"],
            "total_tokens": llm_result["total_tokens"],
        },
    }
