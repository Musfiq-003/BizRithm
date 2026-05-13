# utils/sql_sanitizer.py
"""SQL injection protection and query validation."""
import re
from typing import Tuple
from backend.core.exceptions import SQLInjectionError
from backend.core.logger import logger

# Dangerous SQL patterns
DANGEROUS_PATTERNS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bTRUNCATE\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"--",
    r"/\*.*\*/",
    r"\bUNION\b.*\bSELECT\b",
    r"\bxp_",
    r"\bsp_",
    r";\s*SELECT",
    r"\bINTO\s+OUTFILE\b",
    r"\bLOAD_FILE\b",
]

ALLOWED_STATEMENTS = ["SELECT", "WITH", "EXPLAIN"]


def sanitize_sql(sql: str) -> Tuple[bool, str]:
    """
    Validate SQL for safety.
    Returns (is_safe, cleaned_sql_or_error_message)
    """
    sql_upper = sql.upper().strip()

    # Must start with an allowed statement
    if not any(sql_upper.startswith(stmt) for stmt in ALLOWED_STATEMENTS):
        return False, "Only SELECT queries are allowed"

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            logger.warning(f"Dangerous SQL pattern detected: {pattern}")
            return False, f"Unsafe SQL pattern detected: {pattern}"

    # Remove multiple semicolons (prevent statement stacking)
    cleaned = sql.strip().rstrip(";") + ";"
    if cleaned.count(";") > 1:
        return False, "Multiple SQL statements not allowed"

    return True, cleaned


def add_limit_clause(sql: str, limit: int = 1000) -> str:
    """Ensure query has a LIMIT clause to prevent unbounded results."""
    sql_clean = sql.rstrip(";").strip()
    sql_upper = sql_clean.upper()

    if "LIMIT" not in sql_upper:
        sql_clean += f" LIMIT {limit}"

    return sql_clean + ";"


def validate_table_name(table_name: str) -> bool:
    """Validate table name contains only safe characters."""
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name))


def extract_table_names(sql: str) -> list:
    """Extract table names referenced in a SQL query."""
    pattern = r"\bFROM\b\s+([a-zA-Z_][a-zA-Z0-9_]*)|JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    matches = re.findall(pattern, sql, re.IGNORECASE)
    return [m[0] or m[1] for m in matches]
