from dotenv import load_dotenv
import os

load_dotenv()  

from openai import OpenAI
client = OpenAI()

def llm_lab_analysis(findings):
    abnormal = [f for f in findings if f["status"] != "normal"]

    if not abnormal:
        return "All lab results are within normal range. No concerns flagged."

    findings_text = ""
    for f in abnormal:
        findings_text += f"- {f['lab']}: {f['value']} {f['unit']} (status: {f['status']}, normal: {f['reference_low']}–{f['reference_high']})\n"
        if f["related_observations"]:
            for obs in f["related_observations"]:
                findings_text += f"  Observation: {obs['text']}\n"

    prompt = f"""
You are a clinical data analysis assistant.
IMPORTANT: Do NOT diagnose. Only suggest top 3 possible health concerns.


Abnormal Lab Findings:
{findings_text}

Task: List the top 3 most relevant potential health concerns as a bullet list.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a medical data analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content