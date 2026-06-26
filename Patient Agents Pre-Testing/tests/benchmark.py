import time
import json

from main import route_request


def run_test(request):

    start_time = time.time()

    try:
        result = route_request(request)
        success = True
        error = None

    except Exception as e:
        result = None
        success = False
        error = str(e)

    end_time = time.time()

    return {
        "request": request,
        "success": success,
        "error": error,
        "latency_seconds": round(end_time - start_time, 4),
        "output": result
    }

def run_benchmark_suite():

    test_cases = [
        # FULL PIPELINE
        {"patient_id": "jd-001", "request_type": "full"},
        {"patient_id": "jd-002", "request_type": "full"},

        # PARTIAL QUERIES
        {"patient_id": "jd-001", "request_type": "labs"},
        {"patient_id": "jd-001", "request_type": "risk"},
        {"patient_id": "jd-001", "request_type": "cost"},

        # EDGE CASES
        {"patient_id": "jd-999", "request_type": "full"},  # missing patient
        {"patient_id": "", "request_type": "labs"},        # empty ID
        {"request_type": "risk"},                          # missing ID

        # STRESS TESTS
        {"patient_id": "jd-003", "request_type": "full"},
        {"patient_id": "jd-004", "request_type": "full"},
    ]

    results = []

    total_start = time.time()

    for test in test_cases:
        print(f"Running test: {test}")

        result = run_test(test)
        results.append(result)

    total_end = time.time()

    summary = {
        "total_tests": len(test_cases),
        "total_time": round(total_end - total_start, 4),
        "average_latency": round(
            sum(r["latency_seconds"] for r in results) / len(results),
            4
        ),
        "failures": len([r for r in results if not r["success"]]),
        "results": results
    }

    return summary


def print_summary(summary):

    print("\n================ BENCHMARK SUMMARY ================\n")

    print(f"Total Tests: {summary['total_tests']}")
    print(f"Total Time: {summary['total_time']}s")
    print(f"Average Latency: {summary['average_latency']}s")
    print(f"Failures: {summary['failures']}")

    print("\n================ INDIVIDUAL RESULTS ================\n")

    for r in summary["results"]:
        print(f"Request: {r['request']}")
        print(f"Success: {r['success']}")
        print(f"Latency: {r['latency_seconds']}s")

        if r["error"]:
            print(f"Error: {r['error']}")

        print("-" * 50)