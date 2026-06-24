# ============================================================
# LABS AGENT - run_labs_agent.py
# ============================================================
# INPUTS:  records_output dict from Records Agent (via AGR)
#          contains: patient_id, labs list, observations list
#
# TOOLS:   detect_abnormal()  - rule-based lab range checker
#          context_search()   - links observations to labs
#          llm_analysis()     - GPT call for health concerns
#
# OUTPUT:  dict sent back to AGR containing:
#          - patient_id
#          - findings (each lab with status + related observations)
#          - potential_health_concerns (LLM generated)
# ============================================================

def detect_abnormal(value, low, high):
    if value < low:
        return "low"
    elif value > high:
        return "high"
    return "normal"


def context_search(lab_name, observations):
    related = []
    
    LAB_KEYWORDS = {
        "Hemoglobin": ["fatigue", "anemia", "weakness", "shortness of breath"],
        "Glucose": ["glucose", "blood sugar", "diabetes", "a1c"]
    }

    keywords = LAB_KEYWORDS.get(lab_name, [])

    for obs in observations:
        text = obs["text"].lower()

        if any(keyword in text for keyword in keywords):
            related.append(obs)

    return related


