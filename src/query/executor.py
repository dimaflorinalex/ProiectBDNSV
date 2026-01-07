from src.database.connection import DatabaseConnection
from typing import Tuple, List, Optional

class QueryExecutor:
    """Execute SQL queries"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def execute(self, query: str) -> Tuple[Optional[Tuple[List, List]], Optional[str]]:
        """
        Execute query and return results
        
        Returns:
            Tuple of ((columns, rows), error)
        """
        return self.db.execute_query(query)
    
    def format_results(self, columns: List, rows: List, max_rows: int = 10) -> str:
        """
        Format query results as text
        
        Args:
            columns: Column names
            rows: Result rows
            max_rows: Maximum rows to display
            
        Returns:
            Formatted result string
        """
        if not rows:
            return "No results found."
        
        result_text = f"Found {len(rows)} result(s):\n\n"
        
        # Add column headers
        result_text += " | ".join(str(col) for col in columns) + "\n"
        result_text += "-" * (len(" | ".join(str(col) for col in columns))) + "\n"
        
        # Add rows
        for row in rows[:max_rows]:
            result_text += " | ".join(str(val) if val is not None else "NULL" for val in row) + "\n"
        
        if len(rows) > max_rows:
            result_text += f"\n... and {len(rows) - max_rows} more rows"
        
        return result_text
    
    def format_results_dict(self, columns: List, rows: List) -> List[dict]:
        """
        Format query results as list of dictionaries
        
        Returns:
            List of dictionaries with column names as keys
        """
        if not rows:
            return []
        
        return [dict(zip(columns, row)) for row in rows]
