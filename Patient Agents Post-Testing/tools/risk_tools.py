CONDITION_WEIGHTS = {
    "Hypertension": 15,
    "Diabetes": 15,
    "Coronary Artery Disease": 20,
    "Heart Attack": 25,
    "Chronic Kidney Disease": 20,
    "Heart Failure": 25,
    "Stroke": 20,
    "Type 2 Diabetes": 18,
    "Diabetes": 15,
    "Prediabetes": 8,
    "COPD": 18,
    "Iron Deficiency Anemia": 10,
    "Obesity": 10,
    "Immunosuppression": 22
}


def calculate_risk(risk_context):

    score = 0
    risk_factors = []

    age = risk_context["age"]

    previous_conditions = risk_context.get("previous_conditions", [])

    lifestyle = risk_context.get("lifestyle", {})

    labs = risk_context.get("labs", [])

    if age >= 65:
        score += 20
        risk_factors.append("Age 65 or older")

    if lifestyle.get("smoker"):
        score += 15
        risk_factors.append("Current smoker")

    if lifestyle.get("alcohol_use"):
        score += 5
        risk_factors.append("Alcohol use")

    if lifestyle.get("drug_use"):
        score += 10
        risk_factors.append("Drug use")

    for condition in previous_conditions:

        if condition in CONDITION_WEIGHTS:

            score += CONDITION_WEIGHTS[condition]
            risk_factors.append(condition)

    for lab in labs:

        if lab["name"] == "Glucose" and lab["value"] > 125:
            score += 10
            risk_factors.append("Elevated glucose")

        elif lab["name"] == "Hemoglobin" and lab["value"] < 11:
            score += 5
            risk_factors.append("Low hemoglobin")

        elif lab["name"] == "Creatinine" and lab["value"] > 1.3:
            score += 10
            risk_factors.append("Elevated creatinine")

    score = min(score, 100)

    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Moderate"
    else:
        level = "Low"

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_factors": sorted(set(risk_factors))
    }