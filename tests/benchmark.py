import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmark import load_patient_ids, print_summary, run_benchmark_suite, save_results

if __name__ == "__main__":
    print("Starting healthcare agent benchmark suite (tests/)...\n")
    patients = load_patient_ids()
    results = run_benchmark_suite(patients)
    print_summary(results)
    save_results(results, out_dir=ROOT)

    if results["failed_runs"] > 0 or not results["patient_coverage"]["all_patients_covered"]:
        sys.exit(1)
