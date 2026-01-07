from src.llm.llm_factory import LLMFactory
from src.utils.prompts import PromptTemplates

class SummarizationChain:
    """Summarize SQL results in natural language"""
    
    def __init__(self, model_name: str = None):
        self.llm = LLMFactory.create_llm(model_name)
        self.prompt_templates = PromptTemplates()
    
    def summarize(self, question: str, sql_query: str, results: str) -> str:
        """
        Generate natural language summary of results
        
        Args:
            question: Original natural language question
            sql_query: SQL query that was executed
            results: Formatted results as string
            
        Returns:
            Natural language summary
        """
        
        prompt = self.prompt_templates.SUMMARIZATION_PROMPT.format(
            question=question,
            sql_query=sql_query,
            results=results
        )
        
        summary = self.llm.invoke(prompt).strip()
        return summary
