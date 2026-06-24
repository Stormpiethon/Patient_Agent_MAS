from openai import OpenAI

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
                f"- {obs.get('note', '')}\n"
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