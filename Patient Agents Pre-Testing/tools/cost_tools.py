import json
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine, inspect, text

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "medical_db.db"
SQL_PATH = DATA_DIR / "medical_db.sql"

PROCEDURE_ALIASES = {
    "CBC Panel": "Blood Panel",
}

_engine = None

# Make sure the db has a valid path of access
def ensure_db():
    if DB_PATH.exists():
        return

    with open(SQL_PATH, "r", encoding="utf-8") as sql_file:
        schema_sql = sql_file.read()

    connection = sqlite3.connect(DB_PATH)
    connection.executescript(schema_sql)
    connection.close()

# Get the SQL DB engine connection
def get_engine():
    global _engine

    ensure_db()

    if _engine is None:
        _engine = create_engine(f"sqlite:///{DB_PATH}")

    return _engine

# Get the DB schema to ensure accurate Query generation
def get_db_schema():
    inspector = inspect(get_engine())
    schema_dict = {}

    for table_name in inspector.get_table_names():
        schema_dict[table_name] = []
        for column in inspector.get_columns(table_name):
            schema_dict[table_name].append({
                "name": column["name"],
                "type": str(column["type"])
            })

    return json.dumps(schema_dict, indent=2)

# Ensure Query follows rules set for agent specific tasks
def validate_query(query):
    denied_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP",
        "ALTER", "TRUNCATE", "EXEC", "MERGE"
    ]

    normalized_query = query.upper()

    if not normalized_query.startswith("SELECT"):
        return False

    for keyword in denied_keywords:
        if keyword in normalized_query:
            return False

    return True

# Send the query to the database and return JSON format of output table(s)
def execute_query(query):
    if not validate_query(query):
        return json.dumps({
            "error": "Query validation failed. Forbidden execution syntax."
        })

    try:
        with get_engine().connect() as connection:
            result = connection.execute(text(query))
            rows = [dict(row) for row in result.mappings()]
            return json.dumps(rows, indent=2)
    except Exception as error:
        return json.dumps({
            "error": f"Database Execution Error: {str(error)}"
        })

# Query for medications costs
def _lookup_medication(cost_code=None, name=None):
    with get_engine().connect() as connection:
        if cost_code:
            query = text(
                "SELECT cost_code, medication_name, monthly_cost "
                "FROM medications WHERE cost_code = :cost_code"
            )
            row = connection.execute(
                query, {"cost_code": cost_code}
            ).mappings().first()
        elif name:
            query = text(
                "SELECT cost_code, medication_name, monthly_cost "
                "FROM medications WHERE medication_name = :name"
            )
            row = connection.execute(
                query, {"name": name}
            ).mappings().first()
        else:
            return None

        if row:
            return {
                "cost_code": row["cost_code"],
                "name": row["medication_name"],
                "cost": float(row["monthly_cost"]),
                "cost_period": "monthly"
            }

    return None

# Query for procedure costs
def _lookup_procedure(cost_code=None, name=None):
    if name:
        name = PROCEDURE_ALIASES.get(name, name)

    with get_engine().connect() as connection:
        if cost_code:
            query = text(
                "SELECT cost_code, procedure_name, procedure_cost "
                "FROM procedures WHERE cost_code = :cost_code"
            )
            row = connection.execute(
                query, {"cost_code": cost_code}
            ).mappings().first()
        elif name:
            query = text(
                "SELECT cost_code, procedure_name, procedure_cost "
                "FROM procedures WHERE procedure_name = :name"
            )
            row = connection.execute(
                query, {"name": name}
            ).mappings().first()
        else:
            return None

        if row:
            return {
                "cost_code": row["cost_code"],
                "name": row["procedure_name"],
                "cost": float(row["procedure_cost"]),
                "cost_period": "one-time"
            }

    return None

# Have an LLM create structured output and summary of costs
def analyze_cost_context(cost_context):
    line_items = []

    for medication in cost_context.get("medications", []):
        cost_info = _lookup_medication(
            cost_code=medication.get("cost_code"),
            name=medication.get("name")
        )

        line_items.append({
            "type": "medication",
            "name": medication.get("name"),
            "dose": medication.get("dose"),
            "cost_code": medication.get("cost_code"),
            "unit_cost": cost_info["cost"] if cost_info else None,
            "cost_period": cost_info["cost_period"] if cost_info else None,
            "status": "found" if cost_info else "not_found"
        })

    for procedure in cost_context.get("procedures", []):
        cost_info = _lookup_procedure(
            cost_code=procedure.get("cost_code"),
            name=procedure.get("name")
        )

        line_items.append({
            "type": "procedure",
            "name": procedure.get("name"),
            "cost_code": procedure.get("cost_code"),
            "unit_cost": cost_info["cost"] if cost_info else None,
            "cost_period": cost_info["cost_period"] if cost_info else None,
            "status": "found" if cost_info else "not_found"
        })

    return line_items
