import re

try:
    import sqlglot
    SQLGLOT_AVAILABLE = True
except ImportError:
    SQLGLOT_AVAILABLE = False

class SQLQueryValidator:
    """
    Enforces security, syntax validation, and access control on SQL queries.
    Allows read-only queries (SELECT, WITH) and domain table modifications (DELETE, DROP TABLE, ALTER TABLE DROP COLUMN),
    while strictly protecting internal system tables and preventing SQL injection.
    """
    
    SYSTEM_TABLES = ["nexus_users", "nexus_queries", "nexus_jobs"]
    
    DANGEROUS_KEYWORDS = [
        "ATTACH", "DETACH", "PRAGMA", "SHUTDOWN", "EXEC", "EXECUTE", 
        "GRANT", "REVOKE", "XP_CMDSHELL"
    ]
    
    ALLOWED_START_COMMANDS = ["SELECT", "WITH", "DELETE", "DROP", "ALTER", "INSERT", "UPDATE"]

    @classmethod
    def validate_sql(cls, sql_query: str) -> tuple[bool, str]:
        """
        Validates SQL statement safety and permissions.
        Returns (is_valid: bool, reason: str).
        """
        if not sql_query or not sql_query.strip():
            return False, "Query string is empty."
            
        clean_sql = sql_query.strip().rstrip(";").strip()
        
        # 1. Multi-statement check (prevent semicolon injection)
        if ";" in clean_sql:
            return False, "Security Violation: Multiple SQL statements detected."
            
        upper_sql = clean_sql.upper()
        
        # 2. Check dangerous administrative / OS command keywords
        for kw in cls.DANGEROUS_KEYWORDS:
            pattern = r'\b' + kw + r'\b'
            if re.search(pattern, upper_sql):
                return False, f"Security Violation: Administrative keyword '{kw}' is strictly forbidden."
                
        # 3. Prevent accessing or modifying internal system tables
        for table in cls.SYSTEM_TABLES:
            if re.search(r'\b' + table + r'\b', clean_sql, re.IGNORECASE):
                return False, f"Security Violation: Operation on internal system table '{table}' is strictly restricted."

        # 4. Must start with an allowed command
        starts_allowed = any(upper_sql.startswith(cmd) for cmd in cls.ALLOWED_START_COMMANDS)
        if not starts_allowed:
            allowed_list = ", ".join(cls.ALLOWED_START_COMMANDS)
            return False, f"Invalid Query: Statement must begin with one of: {allowed_list}."

        # 5. AST Parsing using sqlglot if available, else basic validation
        if SQLGLOT_AVAILABLE:
            try:
                parsed = sqlglot.parse_one(clean_sql, read="sqlite")
                if not parsed:
                    return False, "SQL Syntax Error: Unable to parse query AST."
            except Exception as e:
                try:
                    sqlglot.parse_one(clean_sql, read="postgres")
                except Exception:
                    return False, f"SQL Syntax Error: {str(e)}"
        else:
            if clean_sql.count("(") != clean_sql.count(")"):
                return False, "SQL Syntax Error: Unbalanced parentheses in query."
                
        return True, "SQL query passed safety validation."
