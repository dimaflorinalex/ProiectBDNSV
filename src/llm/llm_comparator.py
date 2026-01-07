from typing import List, Dict
from src.llm.llm_factory import LLMFactory
import time

class LLMComparator:
    """Compare SQL generation across different LLMs"""
    
    def __init__(self):
        self.models = LLMFactory.get_available_models()
    
    def compare_models(self, question: str, schema_context: str) -> Dict:
        """
        Compare all models for a given question
        
        Args:
            question: Natural language question
            schema_context: Database schema as string
            
        Returns:
            Dictionary with results from each model
        """
        results = {}
        
        for model in self.models:
            start_time = time.time()
            
            try:
                llm = LLMFactory.create_llm(model)
                
                prompt = f"""Given the database schema:
{schema_context}

Generate a SQL query to answer: {question}

Return ONLY the SQL query, nothing else."""
                
                sql_query = llm.invoke(prompt).strip()
                
                # Clean the query
                sql_query = self._clean_sql(sql_query)
                
                execution_time = time.time() - start_time
                
                results[model] = {
                    "query": sql_query,
                    "execution_time": execution_time,
                    "success": True
                }
            except Exception as e:
                results[model] = {
                    "query": None,
                    "execution_time": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL query from markdown or extra text"""
        # Remove markdown code blocks
        sql = sql.replace("```sql", "").replace("```", "")
        
        # Take only the first SQL statement
        lines = sql.strip().split("\n")
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("--"):
                cleaned_lines.append(line)
        
        return " ".join(cleaned_lines).strip()
