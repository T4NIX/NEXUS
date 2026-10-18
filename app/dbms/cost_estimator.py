import re

class QueryCostEstimator:
    """
    Estimates CPU Burst Time (in ticks/units) and Memory Footprint (in MB)
    for OS Process Scheduling based on query complexity.
    """

    @classmethod
    def estimate_cost(cls, sql_query: str) -> tuple[int, int]:
        """
        Calculates (estimated_burst_time_ticks, memory_mb).
        Base query burst: 2 ticks.
        Simple COUNT(*)/LIMIT 1: 1 tick (fast execution).
        Joins: +2 ticks per JOIN.
        Subqueries / Group By / Order By: +2 ticks each.
        """
        if not sql_query:
            return 3, 64  # Default baseline
            
        upper_sql = sql_query.upper().strip()
        
        # Fast path for DDL / Simple DML
        if upper_sql.startswith("DROP") or upper_sql.startswith("ALTER"):
            return 2, 48
        if upper_sql.startswith("DELETE"):
            return 2, 64
            
        # Fast path for simple queries (e.g., SELECT COUNT(*) FROM students)
        if ("COUNT(" in upper_sql or "LIMIT 1" in upper_sql) and "JOIN" not in upper_sql:
            return 1, 32
            
        base_burst = 2
        base_memory = 64
        
        # Count JOIN clauses
        join_count = len(re.findall(r'\bJOIN\b', upper_sql))
        base_burst += (join_count * 2)
        base_memory += (join_count * 32)
        
        # Aggregations & Groupings
        if "GROUP BY" in upper_sql:
            base_burst += 2
            base_memory += 32
            
        if "ORDER BY" in upper_sql:
            base_burst += 1
            base_memory += 16
            
        if "AVG(" in upper_sql or "SUM(" in upper_sql or "MAX(" in upper_sql or "MIN(" in upper_sql:
            base_burst += 1
            
        # Subqueries
        if upper_sql.count("SELECT") > 1:
            base_burst += 3
            base_memory += 48
            
        # Cap limits
        estimated_burst = max(1, min(15, base_burst))
        estimated_memory = max(32, min(512, base_memory))
        
        return estimated_burst, estimated_memory
