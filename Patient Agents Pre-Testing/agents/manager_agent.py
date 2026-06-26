"""
Manager Agent

Purpose:
    Aggregate outputs from all specialist agents and generate a final
    clinician-facing summary.

Inputs:
    records_output
    labs_output
    risk_output
    cost_output

Outputs:
    final_clinical_summary (string)

Role:
    - Synthesizes structured outputs from sub-agents
    - Does NOT call tools or external APIs directly
    - Produces final human-readable report

Tools:
    llm_manager_summary
"""

from openai import OpenAI

client = OpenAI()


def run_manager_agent(aggregated_context):
    """
    aggregated_context:
        {
            "records": {...} or None,
            "labs": {...} or None,
            "risk": {...} or None,
            "cost": {...} or None
        }
    """

    sections = []

    # Dynamically build prompt sections
    for agent_name in ["records", "labs", "risk", "cost"]:
        data = aggregated_context.get(agent_name)

        if data is not None:
            sections.append(
                f"{agent_name.upper()} OUTPUT:\n{data}"
            )

    context_block = "\n\n".join(sections) if sections else "No agent outputs available."

    prompt = f"""
    You are a clinical decision support summarization system.

    You receive structured outputs from specialist agents.

    Your job is to synthesize ONLY what is provided.

    You must NOT:
    - Invent missing data
    - Repeat full raw outputs
    - Diagnose conditions
    - Add external medical assumptions

    ---

    AVAILABLE AGENT OUTPUTS:

    {context_block}

    ---

    TASK:
    Generate a clinician-facing summary for a nurse or doctor preparing for a patient visit.

    FORMAT:

    1. Patient Overview (2–3 sentences)
    2. Key Clinical Concerns (bullet points)
    3. Risk Summary (short paragraph or "Not provided")
    4. Cost Summary (short paragraph or "Not provided")
    5. Suggested Next Steps (high-level clinical actions only)

    RULES:
    - Only use provided data
    - If a section is missing, explicitly state "Not provided"
    - Prioritize abnormal findings and risk signals
    - Keep concise and clinical
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clinical summarization assistant. "
                    "You synthesize structured medical data into concise, safe clinical reports."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content