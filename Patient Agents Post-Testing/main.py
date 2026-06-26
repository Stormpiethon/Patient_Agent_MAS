import time

from agents.records_agent import get_labs_context, get_cost_context, get_risk_context
from agents.labs_agent import run_labs_agent
from agents.risk_agent import run_risk_agent
from agents.cost_agent import run_cost_agent
from agents.manager_agent import run_manager_agent


def route_request(request):
    """
    request format:
    {
        "patient_id": "jd-001",
        "requested_agents": ["labs", "risk"],
        "chief_complaint": "",
        "nurse_notes": "",
        "smoker": False,
        "alcohol_use": False,
        "drug_use": False
    }
    """

    patient_id = request["patient_id"]
    requested = request.get("requested_agents", [])

    outputs = {}
    timings = {}

    print(f"\nRouting request for patient: {patient_id}")
    print(f"Requested agents: {requested}\n")

    pipeline_start = time.perf_counter()

    # -------------------------
    # RECORDS (always optional base context)
    # -------------------------
    records_context = get_labs_context(
        patient_id,
        request.get("chief_complaint", ""),
        request.get("nurse_notes", "")
    )

    # -------------------------
    # LABS
    # -------------------------
    if "labs" in requested:
        print("[Labs] Running...")
        labs_start = time.perf_counter()
        outputs["labs"] = run_labs_agent(records_context)
        timings["labs"] = round(time.perf_counter() - labs_start, 4)
        print("[Labs] Complete\n")

    # -------------------------
    # RISK
    # -------------------------
    if "risk" in requested:
        print("[Risk] Running...")

        risk_context = get_risk_context(
            patient_id,
            request.get("chief_complaint", ""),
            request.get("nurse_notes", ""),
            request.get("smoker", False),
            request.get("alcohol_use", False),
            request.get("drug_use", False)
        )

        risk_start = time.perf_counter()
        outputs["risk"] = run_risk_agent(risk_context)
        timings["risk"] = round(time.perf_counter() - risk_start, 4)

        print("[Risk] Complete\n")

    # -------------------------
    # COST
    # -------------------------
    if "cost" in requested:
        print("[Cost] Running...")

        cost_context = get_cost_context(patient_id)
        cost_start = time.perf_counter()
        outputs["cost"] = run_cost_agent(cost_context)
        timings["cost"] = round(time.perf_counter() - cost_start, 4)

        print("[Cost] Complete\n")

    # -------------------------
    # RECORDS (optional inclusion in final summary)
    # -------------------------
    if "records" in requested:
        outputs["records"] = records_context

    # -------------------------
    # MANAGER
    # -------------------------
    print("[Manager] Running final synthesis...\n")

    manager_start = time.perf_counter()
    manager_result = run_manager_agent(outputs)
    timings["manager"] = round(time.perf_counter() - manager_start, 4)
    timings["total"] = round(time.perf_counter() - pipeline_start, 4)

    print("[Manager] Complete\n")

    return {
        "final_output": manager_result["summary"],
        "agent_outputs": outputs,
        "timings": timings,
        "manager_metadata": manager_result.get("metadata", {}),
    }



# ============================================================
# PIPELINE EXECUTION (single patient run)
# ============================================================

def run_pipeline(
    patient_id,
    chief_complaint="",
    nurse_notes="",
    smoker=False,
    alcohol_use=False,
    drug_use=False
):

    print("\n==============================")
    print(f"Running pipeline for {patient_id}")
    print("==============================\n")

    # ----------------------------
    # 1. RECORDS AGENT
    # ----------------------------

    print("[1] Records Agent Running...")

    labs_context = get_labs_context(
        patient_id,
        chief_complaint,
        nurse_notes
    )

    risk_context = get_risk_context(
        patient_id,
        chief_complaint,
        nurse_notes,
        smoker,
        alcohol_use,
        drug_use
    )

    cost_context = get_cost_context(patient_id)

    print("[1] Records Agent Complete\n")

    # ----------------------------
    # 2. LABS AGENT
    # ----------------------------

    print("[2] Labs Agent Running...")

    labs_output = run_labs_agent(labs_context)

    print("[2] Labs Agent Complete\n")

    # ----------------------------
    # 3. RISK AGENT
    # ----------------------------

    print("[3] Risk Agent Running...")

    risk_output = run_risk_agent(risk_context)

    print("[3] Risk Agent Complete\n")

    # ----------------------------
    # 4. COST AGENT
    # ----------------------------

    print("[4] Cost Agent Running...")

    cost_output = run_cost_agent(cost_context)

    print("[4] Cost Agent Complete\n")

    # ----------------------------
    # 5. MANAGER AGENT
    # ----------------------------

    print("[5] Manager Agent Running...")

    aggregated_context = {
        "labs": labs_output,
        "risk": risk_output,
        "cost": cost_output
    }

    manager_result = run_manager_agent(aggregated_context)
    final_output = manager_result["summary"]

    print("[5] Manager Agent Complete\n")

    print("========== FINAL OUTPUT ==========\n")
    print(final_output)
    print("\n==================================\n")

    return final_output


# ============================================================
# SMOKE TESTS for debugging
# ============================================================

def run_smoke_tests():

    test_patients = [
        "jd-001",
        "jd-002",
        "jd-003"
    ]

    results = {}

    for pid in test_patients:
        try:
            results[pid] = run_pipeline(pid)
        except Exception as e:
            print(f"ERROR running pipeline for {pid}: {e}")
            results[pid] = None

    return results


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    request = {
        "patient_id": "jd-001",
        "requested_agents": ["labs", "risk", "cost"],
    }

    result = route_request(request)

    print("\nFINAL RESULT:\n")
    print(result["final_output"])
