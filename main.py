import asyncio
import time

from agents.records_agent import get_labs_context, get_cost_context, get_risk_context
from agents.labs_agent import run_labs_agent
from agents.risk_agent import run_risk_agent
from agents.cost_agent import run_cost_agent
from agents.manager_agent import run_manager_agent


async def _run_timed_agent(agent_name, coro):
    start = time.perf_counter()
    result = await coro
    elapsed = round(time.perf_counter() - start, 4)
    return agent_name, result, elapsed


async def route_request(request):
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

    records_context = get_labs_context(
        patient_id,
        request.get("chief_complaint", ""),
        request.get("nurse_notes", ""),
    )

    specialist_tasks = []

    if "labs" in requested:
        print("[Labs] Running...")
        specialist_tasks.append(
            _run_timed_agent("labs", run_labs_agent(records_context))
        )

    if "risk" in requested:
        print("[Risk] Running...")
        risk_context = get_risk_context(
            patient_id,
            request.get("chief_complaint", ""),
            request.get("nurse_notes", ""),
            request.get("smoker", False),
            request.get("alcohol_use", False),
            request.get("drug_use", False),
        )
        specialist_tasks.append(
            _run_timed_agent("risk", run_risk_agent(risk_context))
        )

    if "cost" in requested:
        print("[Cost] Running...")
        cost_context = get_cost_context(patient_id)
        specialist_tasks.append(
            _run_timed_agent("cost", run_cost_agent(cost_context))
        )

    if specialist_tasks:
        specialist_start = time.perf_counter()
        specialist_results = await asyncio.gather(
            *specialist_tasks,
            return_exceptions=True,
        )

        for item in specialist_results:
            if isinstance(item, Exception):
                raise item

            agent_name, result, elapsed = item
            outputs[agent_name] = result
            timings[agent_name] = elapsed
            print(f"[{agent_name.title()}] Complete\n")

        timings["specialists_parallel"] = round(
            time.perf_counter() - specialist_start, 4
        )

    if "records" in requested:
        outputs["records"] = records_context

    print("[Manager] Running final synthesis...\n")

    manager_start = time.perf_counter()
    manager_result = await run_manager_agent(outputs)
    timings["manager"] = round(time.perf_counter() - manager_start, 4)
    timings["total"] = round(time.perf_counter() - pipeline_start, 4)

    print("[Manager] Complete\n")

    return {
        "final_output": manager_result["summary"],
        "agent_outputs": outputs,
        "timings": timings,
        "manager_metadata": manager_result.get("metadata", {}),
        "records_context": records_context,
    }


async def run_pipeline(
    patient_id,
    chief_complaint="",
    nurse_notes="",
    smoker=False,
    alcohol_use=False,
    drug_use=False,
):
    print("\n==============================")
    print(f"Running pipeline for {patient_id}")
    print("==============================\n")

    print("[1] Records Agent Running...")

    labs_context = get_labs_context(
        patient_id,
        chief_complaint,
        nurse_notes,
    )

    risk_context = get_risk_context(
        patient_id,
        chief_complaint,
        nurse_notes,
        smoker,
        alcohol_use,
        drug_use,
    )

    cost_context = get_cost_context(patient_id)

    print("[1] Records Agent Complete\n")

    print("[2-4] Specialist Agents Running in parallel...\n")

    labs_task, risk_task, cost_task = await asyncio.gather(
        _run_timed_agent("labs", run_labs_agent(labs_context)),
        _run_timed_agent("risk", run_risk_agent(risk_context)),
        _run_timed_agent("cost", run_cost_agent(cost_context)),
    )

    _, labs_output, _ = labs_task
    _, risk_output, _ = risk_task
    _, cost_output, _ = cost_task

    print("[2] Labs Agent Complete")
    print("[3] Risk Agent Complete")
    print("[4] Cost Agent Complete\n")

    print("[5] Manager Agent Running...")

    aggregated_context = {
        "labs": labs_output,
        "risk": risk_output,
        "cost": cost_output,
    }

    manager_result = await run_manager_agent(aggregated_context)
    final_output = manager_result["summary"]

    print("[5] Manager Agent Complete\n")

    print("========== FINAL OUTPUT ==========\n")
    print(final_output)
    print("\n==================================\n")

    return final_output


async def run_smoke_tests():
    test_patients = [
        "jd-001",
        "jd-002",
        "jd-003",
    ]

    results = {}

    for pid in test_patients:
        try:
            results[pid] = await run_pipeline(pid)
        except Exception as e:
            print(f"ERROR running pipeline for {pid}: {e}")
            results[pid] = None

    return results


if __name__ == "__main__":
    request = {
        "patient_id": "jd-001",
        "requested_agents": ["labs", "risk", "cost"],
    }

    result = asyncio.run(route_request(request))

    print("\nFINAL RESULT:\n")
    print(result["final_output"])
