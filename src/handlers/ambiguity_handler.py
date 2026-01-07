from src.llm.llm_factory import LLMFactory
from src.utils.prompts import PromptTemplates

class AmbiguityHandler:
    """Handle ambiguous questions"""
    
    def __init__(self, model_name: str = None):
        self.llm = LLMFactory.create_llm(model_name)
        self.prompt_templates = PromptTemplates()
    
    def detect_ambiguity(self, question: str, schema: str) -> bool:
        """
        Detect if question is ambiguous
        
        Args:
            question: Natural language question
            schema: Database schema
            
        Returns:
            True if ambiguous, False otherwise
        """
        
        prompt = f"""Is the following question ambiguous given the database schema?

Question: {question}
Schema: {schema}

Answer with YES or NO only."""
        
        response = self.llm.invoke(prompt).strip().upper()
        return "YES" in response
    
    def clarify(self, question: str, schema: str) -> str:
        """
        Request clarification for ambiguous question
        
        Args:
            question: Ambiguous question
            schema: Database schema
            
        Returns:
            Clarification message with possible interpretations
        """
        
        prompt = self.prompt_templates.CLARIFICATION_PROMPT.format(
            question=question,
            schema=schema
        )
        
        clarification = self.llm.invoke(prompt).strip()
        return clarification
