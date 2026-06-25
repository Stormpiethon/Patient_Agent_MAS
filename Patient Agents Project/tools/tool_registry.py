RECORDS_AGENT_TOOLS = [
    {
        "name": "get_patient_info",
        "description": "Retrieve demographic information for a patient."
    },
    {
        "name": "get_labs",
        "description": "Retrieve laboratory test results for a patient."
    },
    {
        "name": "get_observations",
        "description": "Retrieve provider notes and clinical observations."
    },
    {
        "name": "get_medications",
        "description": "Retrieve prescribed medications."
    },
    {
        "name": "get_procedures",
        "description": "Retrieve completed medical procedures."
    }
]

LABS_AGENT_TOOLS = [
    {
        "name": "analyze_labs_context",
        "description": (
            "Analyze laboratory results received from the Records Agent. "
            "Identify abnormal values and return structured findings."
        )
    },
    {
        "name": "llm_lab_analysis",
        "description": (
            "Analyze abnormal laboratory findings and clinical observations. "
            "Return the top 3 potential health concerns a physician may wish "
            "to investigate further. Does not diagnose or recommend treatment."
        )
    }
]

COST_AGENT_TOOLS = [
    {
        "name": "analyze_cost_context",
        "description": (
            "Resolve medication and procedure costs from the cost database "
            "using cost codes or item names from the Records Agent context."
        )
    },
    {
        "name": "llm_cost_summary",
        "description": (
            "Generate a natural-language summary of the patient's estimated "
            "medication and procedure costs. Does not provide financial advice."
        )
    },
    {
        "name": "get_db_schema",
        "description": "Retrieve the cost database schema for reference."
    },
    {
        "name": "execute_query",
        "description": (
            "Execute a validated read-only SQL query against the cost database."
        )
    }
]