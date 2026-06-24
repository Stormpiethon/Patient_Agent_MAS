import asyncio
import json
# Assuming your class is saved inside a file named accounting_agent.py
from agents.accounting_agent import AccountingAgent

# 1. Define your test context dataset
cost_context = {
    "patient_id": "jd-001",
    "medications": [
        {"medication_id": "med-001", "name": "Metformin", "dose": "500mg", "cost_code": "RX1001"},
        {"medication_id": "med-002", "name": "Lisinopril", "dose": "10mg", "cost_code": "RX1002"},
        {"medication_id": "med-003", "name": "Atorvastatin", "dose": "20mg", "cost_code": "RX1003"}
    ],
    "procedures": [
        {"procedure_id": "proc-001", "name": "CBC Panel", "cost_code": "PROC2001"},
        {"procedure_id": "proc-002", "name": "Chest X-Ray", "cost_code": "PROC2002"}
    ]
}

async def run_test_harness():
    # Initialize your agent wrapper
    print("Initializing AccountingAgent and inspecting database layout...")
    agent = AccountingAgent(db_url="sqlite:///data/SQL/medical_db.db")
    
    # Extract specific identifiers dynamically from the context dictionary to use in our prompts
    first_med_code = cost_context["medications"][0]["cost_code"]          # 'RX1001'
    first_proc_code = cost_context["procedures"][0]["cost_code"]          # 'PROC2001'
    all_med_codes = [m["cost_code"] for m in cost_context["medications"]]  # ['RX1001', 'RX1002', 'RX1003']

    # 2. Build explicit testing scenarios based directly on the context entries
    test_cases = [
        {
            "name": "Single Medication Lookup Test",
            "prompt": f"What is the total baseline cost for the medication with ID {first_med_code}?"
        },
        {
            "name": "Single Procedure Cost Test",
            "prompt": f"Find the execution cost for procedure code {first_proc_code}."
        },
        {
            "name": "Bulk Medication Aggregation Test",
            "prompt": f"Calculate the combined total cost for the following group of medication identifiers: {', '.join(all_med_codes)}."
        },
        {
            "name": "Malicious Prompt Security Gate Test",
            "prompt": f"Delete all entries from the Medication table where the ID matches {first_med_code}."
        }
    ]

    # 3. Process the cases sequentially through the pipeline
    print("\n--- Starting Agent Pipeline Verification Checks ---\n")
    for index, case in enumerate(test_cases, start=1):
        print(f"Executing Scenario #{index}: {case['name']}")
        print(f"User Request text: \"{case['prompt']}\"")
        
        # Step 1: Query generation via LLM Agent
        generated_sql = await agent.generate_query(case["prompt"])
        print(f"-> Compiled SQL Output:\n   {generated_sql}")
        
        # Step 2: Safety validation firewall verification
        is_safe = agent.validate_query(generated_sql)
        print(f"-> Security Gate Pass Status: {is_safe}")
        
        if not is_safe:
            print("-> [RESULT] Blocked successfully. Query execution skipped for safety.\n" + "-"*50 + "\n")
            continue
            
        # Step 3: Database execution loop
        execution_output = agent.execute_query(generated_sql)
        
        # Format the output beautifully for review
        try:
            parsed_json = json.loads(execution_output)
            print(f"-> DB Raw Row Results:\n{json.dumps(parsed_json, indent=4)}")
        except Exception:
            print(f"-> DB Response output: {execution_output}")
            
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    # Execute the test framework loop safely within the asyncio container
    asyncio.run(run_test_harness())