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