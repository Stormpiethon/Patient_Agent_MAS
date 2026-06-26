# Compile relevant records data and create labs context
def analyze_labs_context(labs_context):
    findings = []

    for lab in labs_context.get("labs", []):

        status = "normal"

        if lab["value"] < lab["reference_low"]:
            status = "low"

        elif lab["value"] > lab["reference_high"]:
            status = "high"

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