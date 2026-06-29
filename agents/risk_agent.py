from tools.risk_tools import calculate_risk
from tools.llm_tools import llm_risk_summary


async def run_risk_agent(risk_context):
    risk_result = calculate_risk(risk_context)

    summary = await llm_risk_summary(
        risk_context=risk_context,
        risk_score=risk_result["risk_score"],
        risk_level=risk_result["risk_level"],
        risk_factors=risk_result["risk_factors"],
    )

    return {
        "agent": "risk_agent",
        "patient": {
            "patient_id": risk_context["patient_id"],
            "name": risk_context["name"],
            "age": risk_context["age"],
            "gender": risk_context["gender"],
        },
        "analysis": {
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "risk_factors": risk_result["risk_factors"],
            "summary": summary["risk_summary"],
        },
        "metadata": {
            "prompt_tokens": summary["prompt_tokens"],
            "completion_tokens": summary["completion_tokens"],
            "total_tokens": summary["total_tokens"],
        },
    }
