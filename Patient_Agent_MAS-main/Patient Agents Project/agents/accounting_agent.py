import json
import os
import re
import asyncio
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

load_dotenv()

class AccountingAgent:
    def __init__(self, db_url: str = "sqlite:///data/SQL/medical_db.db"):
        # Establish the engine; connection pooling handles the lifecycle
        self.engine = create_engine(db_url)
        self.schema = self.get_db_schema()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.agent = Agent(
            name = "Cost Agent",
            model = self.model,
            instructions = f"""
You are an expert Accounting Cost Agent. Your single goal is to read the database schema provided below and transform natural language data requests into explicit SQL queries.

DATABASE SCHEMA:
{self.schema}

MAPPING RULES:
- Alphanumeric medication identifiers (e.g., 'RX1001') correspond directly to 'Medication.MedicationID'.
- Alphanumeric procedure identifiers (e.g., 'PROC2001') correspond directly to 'ProceduresCost.ProcedureID'.

CRITICAL INSTRUCTIONS:
1. Always run your compiled queries through the 'execute_query' tool to get live row details.
2. Do NOT use broad wildcards like SELECT *; always state the specific cost metrics needed.
3. Only use SELECT statements. 
""",
            # Hand the execution capability directly to the Agent runner loop
            tools=[self.execute_query]
    )

    def get_db_schema(self) -> str:
        """Helper tool: Extracts metadata so the LLM knows the schema."""
        inspector = inspect(self.engine)
        schema_dict = {}

        for table_name in inspector.get_table_names():
            schema_dict[table_name] = []
            for column in inspector.get_columns(table_name):
                schema_dict[table_name].append({
                    "name": column["name"],
                    "type": str(column["type"])
                })


        return json.dumps(schema_dict, indent = 2)
      
    async def generate_query(self, user_input: str) -> str:
        """LLM tool: Uses the OpenAI SDK to reason and construct a SQL string."""
        result = await Runner.run(self.agent, user_input)
        raw_query = result.final_output.strip()

        raw_query = re.sub(r"```sql\s*", "", raw_query, flags=re.IGNORECASE)
        raw_query = re.sub(r"```\s*$", "", raw_query)

        return raw_query.strip()

    def validate_query(self, query: str) -> bool:
        denied_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "EXEC", "MERGE"]

        normalized_query = query.upper()

        if not normalized_query.startswith("SELECT"):
            return False

        for keyword in denied_keywords:
            if keyword in normalized_query:
                return False

        return True
  

    @function_tool
    def execute_query(self, query: str) -> str:
        """Database tool: Safely opens a connection, executes text, and returns data."""
        if not self.validate_query(query):
            return json.dumps({"error": "Query validation failed. Forbidden execution syntax."})
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                rows = [dict(row) for row in result.mappings()]
                return json.dumps(rows, indent = 2)
            
        except Exception as e:
            return json.dumps({"error": f"Database Execution Error: {str(e)}"})