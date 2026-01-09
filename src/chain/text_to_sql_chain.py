from src.database.connection import DatabaseConnection
from src.query.generator import QueryGenerator
from src.query.executor import QueryExecutor
from src.query.validator import SQLValidator
from src.chain.summarization_chain import SummarizationChain
from typing import Dict, Optional
from config.settings import Settings

class TextToSQLChain:
    """Main chain for Text-To-SQL pipeline"""
    
    def __init__(self, db_path: str = None, model_name: str = None):
        self.db = DatabaseConnection(db_path)
        self.db.connect()
        
        self.generator = QueryGenerator(model_name)
        self.executor = QueryExecutor(self.db)
        self.validator = SQLValidator()
        self.summarizer = SummarizationChain(model_name)
        
        self.schema = self.db.get_schema()
    
    def run(self, question: str, max_retries: int = None, 
            use_few_shot: bool = False, use_chain_of_thought: bool = False,
            use_feedback_learning: bool = True) -> Dict:
        """
        Run the complete Text-To-SQL chain
        
        Args:
            question: Natural language question
            max_retries: Maximum retry attempts (defaults to Settings.MAX_RETRIES)
            use_few_shot: Use few-shot prompting
            use_chain_of_thought: Use chain-of-thought prompting
            use_feedback_learning: Use feedback learning (enabled by default)
            
        Returns:
            Dictionary with results including question, query, results, summary, errors
        """
        
        if max_retries is None:
            max_retries = Settings.MAX_RETRIES
        
        result = {
            "question": question,
            "sql_query": None,
            "results": None,
            "summary": None,
            "error": None,
            "attempts": []
        }
        
        attempt = 0
        
        while attempt <= max_retries:
            try:
                # Generate SQL
                if attempt == 0:
                    sql_query = self.generator.generate(
                        question, 
                        self.schema,
                        use_few_shot=use_few_shot,
                        use_chain_of_thought=use_chain_of_thought,
                        use_feedback_learning=use_feedback_learning
                    )
                else:
                    # Regenerate with error feedback
                    last_error = result["attempts"][-1]["error"]
                    last_query = result["attempts"][-1]["query"]
                    sql_query = self.generator.regenerate_with_error(
                        question, self.schema, last_query, last_error
                    )
                
                result["attempts"].append({
                    "attempt": attempt + 1,
                    "query": sql_query,
                    "error": None
                })
                
                # Validate syntax
                is_valid, validation_error = self.validator.validate_syntax(sql_query)
                
                if not is_valid:
                    result["attempts"][-1]["error"] = validation_error
                    attempt += 1
                    continue
                
                # Execute query
                query_result, execution_error = self.executor.execute(sql_query)
                
                if execution_error:
                    result["attempts"][-1]["error"] = execution_error
                    attempt += 1
                    continue
                
                # Success!
                columns, rows = query_result
                result["sql_query"] = sql_query
                result["results"] = {
                    "columns": columns,
                    "rows": rows
                }
                
                # Format results
                formatted_results = self.executor.format_results(columns, rows)
                
                # Summarize
                result["summary"] = self.summarizer.summarize(
                    question, sql_query, formatted_results
                )
                
                break
                
            except Exception as e:
                if result["attempts"]:
                    result["attempts"][-1]["error"] = str(e)
                else:
                    result["attempts"].append({
                        "attempt": attempt + 1,
                        "query": None,
                        "error": str(e)
                    })
                attempt += 1
        
        if result["sql_query"] is None:
            result["error"] = "Failed to generate valid SQL after maximum retries"
        
        return result
    
    def close(self):
        """Close database connection"""
        self.db.disconnect()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
