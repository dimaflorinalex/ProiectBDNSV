import sqlparse
from typing import Tuple, Optional

class SQLValidator:
    """Validate SQL queries"""
    
    def validate_syntax(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL syntax
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse the query
            parsed = sqlparse.parse(query)
            
            if not parsed:
                return False, "Empty or invalid query"
            
            # Check if it's a SELECT statement
            first_stmt = parsed[0]
            first_token_type = first_stmt.get_type()
            
            if first_token_type != 'SELECT':
                # Check the actual tokens
                for token in first_stmt.tokens:
                    if token.ttype is None and hasattr(token, 'value'):
                        if token.value.upper().startswith('SELECT'):
                            return True, None
                return False, "Only SELECT queries are allowed"
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitize and format SQL query
        
        Raises:
            ValueError if dangerous keywords detected
        """
        # Remove dangerous keywords
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
        
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Dangerous keyword detected: {keyword}")
        
        # Format the query
        formatted = sqlparse.format(query, reindent=True, keyword_case='upper')
        return formatted
    
    def clean_sql(self, sql: str) -> str:
        """Clean SQL query from markdown or extra text"""
        # Remove markdown code blocks
        sql = sql.replace("```sql", "").replace("```", "")
        
        # Remove extra whitespace and newlines
        lines = sql.strip().split("\n")
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("--"):
                cleaned_lines.append(line)
        
        return " ".join(cleaned_lines).strip()
