from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# Creat an AI augmented summary of lab agent findings
from openai import OpenAI

client = OpenAI()


from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def llm_lab_analysis(
    findings,
    age,
    gender,
    previous_conditions,
    observations,
    encounter
):

    abnormal = [
        f for f in findings
        if f["status"] != "normal"
    ]

    if not abnormal:
        return {
            "health_concerns": "No abnormal laboratory findings identified.",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    findings_text = ""

    for lab in abnormal:

        findings_text += (
            f"- {lab['name']}: "
            f"{lab['value']} {lab['unit']} "
            f"(Reference: {lab['reference_low']}–{lab['reference_high']}, "
            f"Status: {lab['status']})\n"
        )

    observations_text = "\n".join(
        f"- {obs.get('text') or obs.get('note', '')}"
        for obs in observations
    )

    conditions_text = ", ".join(previous_conditions)

    prompt = f"""
    You are a clinical decision support assistant.

    Patient Information

    Age:
    {age}

    Gender:
    {gender}

    Previous Conditions:
    {conditions_text if conditions_text else "None documented"}

    Current Encounter

    Chief Complaint:
    {encounter.get("chief_complaint", "")}

    Nurse Notes:
    {encounter.get("nurse_notes", "")}

    Abnormal Laboratory Findings

    {findings_text}

    Clinical Observations

    {observations_text if observations_text else "None"}

    Task

    Based ONLY on the information above:

    Return ONLY the three most likely health concerns a physician may wish
    to investigate.

    Do NOT diagnose.

    Do NOT recommend medications.

    Do NOT recommend treatment.

    Keep each concern to one concise sentence.

    If there is insufficient evidence, explicitly state that.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content":
                "You summarize structured medical information for clinicians."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "health_concerns":
            response.choices[0].message.content,

        "prompt_tokens":
            response.usage.prompt_tokens,

        "completion_tokens":
            response.usage.completion_tokens,

        "total_tokens":
            response.usage.total_tokens
    }


# Create a summary of the cost agent outputs
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def llm_cost_analysis(
    medications,
    procedures,
    total_cost
):

    medication_text = "\n".join(
        f"- {med['name']}"
        for med in medications
    )

    procedure_text = "\n".join(
        f"- {proc['name']}"
        for proc in procedures
    )

    prompt = f"""
    You are a healthcare cost summarization assistant.

    Patient Billing Information

    Medications

    {medication_text if medication_text else "None"}

    Procedures

    {procedure_text if procedure_text else "None"}

    Estimated Total Cost

    ${total_cost:.2f}

    Task

    Generate a concise cost summary.

    Requirements

    - Summarize only the supplied information.
    - Do NOT estimate insurance coverage.
    - Do NOT recommend treatments.
    - Do NOT invent prices.
    - Mention the total estimated cost.
    - Keep the response under 100 words.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content":
                "You summarize healthcare billing information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "cost_summary":
            response.choices[0].message.content,

        "prompt_tokens":
            response.usage.prompt_tokens,

        "completion_tokens":
            response.usage.completion_tokens,

        "total_tokens":
            response.usage.total_tokens
    }


# Finalize the risk evaluation with AI summary
def llm_risk_summary(
    risk_context,
    risk_factors,
    risk_score,
    risk_level
):

    factors_text = "\n".join(
        [f"- {factor}" for factor in risk_factors]
    )

    conditions_text = "\n".join(
        risk_context.get("previous_conditions", [])
    )

    prompt = f"""
    You are a healthcare risk assessment assistant.

    IMPORTANT:
    - Do NOT diagnose.
    - Do NOT predict life expectancy.
    - Do NOT recommend treatment.

    Patient Information:

    Age:
    {risk_context.get("age", "Unknown")}

    Gender:
    {risk_context.get("gender", "Unknown")}

    Known Conditions:
    {conditions_text}

    Identified Risk Factors:
    {factors_text}

    Calculated Risk Score:
    {risk_score}

    Risk Level:
    {risk_level}

    Task:

    Explain the calculated risk using ONLY the supplied information.

    Do NOT invent additional risk factors.

    Do NOT diagnose.

    Do NOT recommend medications.

    Do NOT recommend treatment.

    Keep the explanation under 100 words.

    Provide:

    1. Brief overall risk summary
    2. Most significant contributing factors
    3. Positive indicators if any exist
    4. Topics a clinician may want to discuss

    OUTPUT FORMAT EXAMPLE:
    {{
    "risk_level_summary": "Low | Moderate | High",
    "key_drivers": [
        "factor 1",
        "factor 2",
        "factor 3"
    ],
    "one_line_summary": "short clinical-style summary. 2-3 sentences"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a medical risk assessment assistant. "
                    "You provide informational summaries only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return {
        "risk_summary": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }