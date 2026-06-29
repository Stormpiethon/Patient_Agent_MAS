import asyncio
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from main import route_request
from metrics import MetricsCollector, aggregate_results
from tools.lab_tools import analyze_labs_context

RESULTS_JSON = ROOT / "benchmark_results.json"
RESULTS_CSV = ROOT / "benchmark_results.csv"

AGENT_CONFIGS = {
    "labs": ["labs"],
    "risk": ["risk"],
    "cost": ["cost"],
    "labs_risk": ["labs", "risk"],
    "labs_risk_cost": ["labs", "risk", "cost"],
    "full_pipeline": ["labs", "risk", "cost"],
}


def load_patient_ids() -> list[str]:
    data_dir = ROOT / "data"
    patient_ids = sorted(path.stem for path in data_dir.glob("jd-*.json"))
    if not patient_ids:
        raise FileNotFoundError(f"No patient JSON files found in {data_dir}")
    return patient_ids


def load_patient(patient_id: str) -> dict:
    patient_path = ROOT / "data" / f"{patient_id}.json"
    with open(patient_path, "r", encoding="utf-8") as patient_file:
        return json.load(patient_file)


def count_abnormal_labs(patient_id: str) -> int:
    patient_path = ROOT / "data" / f"{patient_id}.json"
    if not patient_path.exists():
        return 0

    patient = load_patient(patient_id)
    abnormal_count = 0
    for lab in patient.get("labs", []):
        status = analyze_labs_context(
            lab["value"],
            lab["reference_low"],
            lab["reference_high"],
        )
        if status != "normal":
            abnormal_count += 1

    return abnormal_count


def describe_patient_scenario(patient_id: str) -> str:
    patient = load_patient(patient_id)
    labs = patient.get("labs", [])
    observations = patient.get("observations", [])
    conditions = patient.get("previous_conditions", [])

    tags = []
    if not labs:
        tags.append("missing_labs")
    if not observations:
        tags.append("missing_observations")
    if not conditions:
        tags.append("no_conditions")
    else:
        tags.append("has_conditions")

    abnormal_count = count_abnormal_labs(patient_id)
    if labs and abnormal_count == 0:
        tags.append("all_normal_labs")
    elif abnormal_count > 0:
        tags.append(f"abnormal_labs_{abnormal_count}")

    return ",".join(tags)


def extract_tokens(agent_output: dict | None) -> dict:
    if not agent_output:
        return {}
    return agent_output.get("metadata", {})


def run_single_benchmark(patient_id: str, requested_agents: list[str], config_name: str) -> dict:
    metrics = MetricsCollector()
    request = {
        "patient_id": patient_id,
        "requested_agents": requested_agents,
        "chief_complaint": "",
        "nurse_notes": "",
        "smoker": False,
        "alcohol_use": False,
        "drug_use": False,
    }

    print(f"  Running {patient_id} | config={config_name} | agents={requested_agents}")

    metrics.start_timer("total")
    try:
        result = asyncio.run(route_request(request))
        metrics.end_timer("total")

        timings = result.get("timings", {})
        for agent in ("labs", "risk", "cost", "manager", "specialists_parallel"):
            if agent in timings:
                metrics.timings[agent] = timings[agent]

        outputs = result.get("agent_outputs", {})
        metrics.record_tokens("labs", extract_tokens(outputs.get("labs")))
        metrics.record_tokens("risk", extract_tokens(outputs.get("risk")))
        metrics.record_tokens("cost", extract_tokens(outputs.get("cost")))
        metrics.record_tokens("manager", result.get("manager_metadata"))

        row = metrics.to_flat_row(patient_id, requested_agents)
        row["config_name"] = config_name
        row["patient_scenario"] = describe_patient_scenario(patient_id)
        row["abnormal_lab_count"] = count_abnormal_labs(patient_id)
        row["output_size_chars"] = len(result.get("final_output", "") or "")
        return row

    except Exception as error:
        metrics.end_timer("total")
        row = metrics.to_flat_row(patient_id, requested_agents)
        row["config_name"] = config_name
        row["patient_scenario"] = describe_patient_scenario(patient_id)
        row["abnormal_lab_count"] = count_abnormal_labs(patient_id)
        row["success"] = False
        row["error"] = str(error)
        print(f"    FAILED: {error}")
        return row


def build_patient_coverage(rows: list[dict], patients: list[str]) -> dict:
    tested_patients = {row["patient_id"] for row in rows}
    missing_patients = [patient_id for patient_id in patients if patient_id not in tested_patients]
    runs_per_patient = {
        patient_id: sum(1 for row in rows if row["patient_id"] == patient_id)
        for patient_id in patients
    }

    return {
        "expected_patients": patients,
        "patients_tested": sorted(tested_patients),
        "missing_patients": missing_patients,
        "all_patients_covered": len(missing_patients) == 0,
        "runs_per_patient": runs_per_patient,
    }


def run_benchmark_suite(patients: list[str] | None = None) -> dict:
    patients = patients or load_patient_ids()
    rows = []
    run_started_at = datetime.now(timezone.utc).isoformat()

    print(f"Patients in suite: {len(patients)}")
    print(f"Configurations:    {len(AGENT_CONFIGS)}")
    print(f"Total runs:        {len(patients) * len(AGENT_CONFIGS)}\n")

    for config_name, agents in AGENT_CONFIGS.items():
        print(f"\n=== Config: {config_name} ({agents}) ===")
        for patient_id in patients:
            rows.append(run_single_benchmark(patient_id, agents, config_name))

    summary = aggregate_results(rows)
    summary["run_started_at"] = run_started_at
    summary["run_completed_at"] = datetime.now(timezone.utc).isoformat()
    summary["patients_in_suite"] = patients
    summary["configurations"] = AGENT_CONFIGS
    summary["patient_coverage"] = build_patient_coverage(rows, patients)
    return summary


def save_results(summary: dict, out_dir: Path = ROOT) -> None:
    json_path = out_dir / RESULTS_JSON.name
    csv_path = out_dir / RESULTS_CSV.name

    # Always replace prior results on each run.
    if json_path.exists():
        json_path.unlink()
    if csv_path.exists():
        csv_path.unlink()

    with open(json_path, "w", encoding="utf-8") as output_file:
        json.dump(summary, output_file, indent=2)

    if summary["rows"]:
        fieldnames = list(summary["rows"][0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary["rows"])
    else:
        csv_path.write_text("", encoding="utf-8")

    print(f"\nSaved: {json_path}")
    print(f"Saved: {csv_path}")


def print_summary(summary: dict) -> None:
    coverage = summary["patient_coverage"]

    print("\n" + "=" * 50)
    print("BENCHMARK SUMMARY")
    print("=" * 50)
    print(f"Total runs:       {summary['total_runs']}")
    print(f"Successful:       {summary['successful_runs']}")
    print(f"Failed:           {summary['failed_runs']}")
    print(f"Avg latency:      {summary['avg_total_latency']}s")
    print(f"Avg tokens/agent: {summary['avg_tokens_by_agent']}")
    print(f"Patients covered: {len(coverage['patients_tested'])}/{len(coverage['expected_patients'])}")

    if coverage["missing_patients"]:
        print(f"Missing patients: {coverage['missing_patients']}")


if __name__ == "__main__":
    print("Starting healthcare agent benchmark suite...\n")
    patients = load_patient_ids()
    results = run_benchmark_suite(patients)
    print_summary(results)
    save_results(results)

    if results["failed_runs"] > 0 or not results["patient_coverage"]["all_patients_covered"]:
        sys.exit(1)
