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

AVAILABLE_AGENTS = [
    {
        "name": "Records Agent",
        "description": "Retrieve patient information."
    },
    {
        "name": "Labs Agent",
        "description": "Analyze laboratory findings."
    },
    {
        "name": "Cost Agent",
        "description": "Estimate treatment costs."
    }
]

RISK_AGENT_TOOLS = [
    {
        "name": "extract_risk_factors",
        "description": (
            "Extract risk factors from patient conditions, "
            "laboratory results, and survey data."
        )
    },
    {
        "name": "calculate_risk_score",
        "description": (
            "Calculate a numerical risk score using identified "
            "risk factors."
        )
    },
    {
        "name": "determine_risk_level",
        "description": (
            "Convert a numerical risk score into a "
            "Low, Moderate, or High risk level."
        )
    },
    {
        "name": "llm_risk_summary",
        "description": (
            "Generate a clinician-facing summary of patient "
            "risk factors and overall risk level."
        )
    }
]