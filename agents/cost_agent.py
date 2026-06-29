from tools.cost_tools import analyze_cost_context
from tools.llm_tools import llm_cost_analysis


async def run_cost_agent(cost_context):
    line_items = analyze_cost_context(cost_context)

    total_cost = sum(
        item["unit_cost"]
        for item in line_items
        if item["unit_cost"] is not None
    )

    cost_summary = await llm_cost_analysis(
        medications=cost_context.get("medications", []),
        procedures=cost_context.get("procedures", []),
        total_cost=total_cost,
    )

    return {
        "agent": "cost_agent",
        "patient": {
            "patient_id": cost_context["patient_id"],
            "name": cost_context["name"],
            "age": cost_context["age"],
            "gender": cost_context["gender"],
        },
        "analysis": {
            "line_items": line_items,
            "total_cost": total_cost,
            "summary": cost_summary["cost_summary"],
        },
        "metadata": {
            "prompt_tokens": cost_summary["prompt_tokens"],
            "completion_tokens": cost_summary["completion_tokens"],
            "total_tokens": cost_summary["total_tokens"],
        },
    }
