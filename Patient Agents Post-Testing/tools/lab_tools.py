def analyze_labs_context(value, reference_low=None, reference_high=None):
    if reference_low is not None and reference_high is not None:
        if value < reference_low:
            return "low"
        if value > reference_high:
            return "high"
        return "normal"

    labs_context = value
    findings = []

    for lab in labs_context.get("labs", []):
        status = analyze_labs_context(
            lab["value"],
            lab["reference_low"],
            lab["reference_high"],
        )

        findings.append({
            "lab_id": lab["lab_id"],
            "lab": lab["name"],
            "value": lab["value"],
            "unit": lab["unit"],
            "reference_low": lab["reference_low"],
            "reference_high": lab["reference_high"],
            "status": status
        })

    return findings
