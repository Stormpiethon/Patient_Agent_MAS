from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def llm_lab_analysis(findings, observations=None, age=None, gender=None):

    abnormal = [f for f in findings if f["status"] != "normal"]

    if not abnormal:
        return "No abnormal laboratory findings detected."

    findings_text = ""

    for f in abnormal:
        findings_text += (
            f"- {f['lab']}: "
            f"{f['value']} {f['unit']} "
            f"(status: {f['status']}, "
            f"normal range: "
            f"{f['reference_low']} - {f['reference_high']})\n"
        )

    observation_text = ""

    if observations:

        for obs in observations:

            observation_text += (
                f"- {obs.get('note') or obs.get('text', '')}\n"
            )

    prompt = f"""
    You are a clinical data analysis assistant.

    IMPORTANT:
    - Do not diagnose.
    - Do not recommend treatment.
    - Do not claim certainty.
    - Only provide the 3 most likely health concerns that a physician may wish to investigate further.

    Patient Context

    Age: {age}
    Gender: {gender}

    Abnormal Laboratory Findings:

    {findings_text}

    Clinical Observations:

    {observation_text}

    Return:

    - Concern 1
    - Concern 2
    - Concern 3
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clinical data analysis assistant. "
                    "You identify possible areas of concern from "
                    "laboratory findings and clinical observations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def llm_cost_summary(line_items, total_cost, patient_id=None):

    if not line_items:
        return "No medications or procedures found for cost analysis."

    items_text = ""

    for item in line_items:
        if item["status"] == "found":
            items_text += (
                f"- {item['type'].title()}: {item['name']} "
                f"(${item['unit_cost']:.2f}, {item['cost_period']})\n"
            )
        else:
            items_text += (
                f"- {item['type'].title()}: {item['name']} "
                f"(cost not found in database)\n"
            )

    prompt = f"""
    You are a healthcare cost analysis assistant.

    IMPORTANT:
    - Do not provide financial advice.
    - Do not recommend changes to treatment.
    - Summarize the patient's estimated costs clearly and concisely.

    Patient ID: {patient_id}

    Cost Breakdown:

    {items_text}

    Total Estimated Cost: ${total_cost:.2f}

    Provide a brief 2-3 sentence summary of the patient's estimated
    medication and procedure costs.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a healthcare cost analysis assistant. "
                    "You summarize medication and procedure costs "
                    "based on structured billing data."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content