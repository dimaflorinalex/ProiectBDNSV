from src.llm.llm_factory import LLMFactory
from src.utils.prompts import PromptTemplates
from src.query.validator import SQLValidator
from typing import Optional

class QueryGenerator:
    """Generate SQL queries from natural language"""
    
    def __init__(self, model_name: str = None):
        self.llm = LLMFactory.create_llm(model_name)
        self.validator = SQLValidator()
        self.prompt_templates = PromptTemplates()
    
    def generate(self, question: str, schema: str, use_few_shot: bool = False, 
                 use_chain_of_thought: bool = False) -> str:
        """
        Generate SQL query from question
        
        Args:
            question: Natural language question
            schema: Database schema as string
            use_few_shot: Use few-shot prompting
            use_chain_of_thought: Use chain-of-thought prompting
            
        Returns:
            Generated SQL query
        """
        
        if use_chain_of_thought:
            prompt = self.prompt_templates.CHAIN_OF_THOUGHT_PROMPT.format(
                schema=schema,
                question=question
            )
        elif use_few_shot:
            prompt = self.prompt_templates.FEW_SHOT_PROMPT.format(
                schema=schema,
                question=question
            )
        else:
            prompt = self.prompt_templates.SQL_GENERATION_PROMPT.format(
                schema=schema,
                question=question
            )
        
        sql_query = self.llm.invoke(prompt).strip()
        
        # Clean the query
        sql_query = self.validator.clean_sql(sql_query)
        
        return sql_query
    
    def regenerate_with_error(self, question: str, schema: str, 
                            original_query: str, error: str) -> str:
        """
        Regenerate query after error
        
        Args:
            question: Original question
            schema: Database schema
            original_query: Query that failed
            error: Error message
            
        Returns:
            Corrected SQL query
        """
        
        prompt = self.prompt_templates.ERROR_CORRECTION_PROMPT.format(
            sql_query=original_query,
            error=error,
            schema=schema
        )
        
        sql_query = self.llm.invoke(prompt).strip()
        sql_query = self.validator.clean_sql(sql_query)
        
        return sql_query
