try:
    from langchain_ollama import OllamaLLM
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM
from config.settings import Settings

class LLMFactory:
    """Factory to create Ollama LLM instances"""
    
    @staticmethod
    def create_llm(model_name: str = None, temperature: float = None):
        """
        Create an Ollama LLM instance
        
        Args:
            model_name: Name of the Ollama model to use (e.g., 'llama3:latest')
            temperature: Temperature for generation (0.0-1.0)
            
        Returns:
            Ollama LLM instance
        """
        if model_name is None:
            model_name = Settings.DEFAULT_MODEL
        
        if temperature is None:
            temperature = Settings.TEMPERATURE
        
        return OllamaLLM(
            model=model_name,
            base_url=Settings.OLLAMA_BASE_URL,
            temperature=temperature,
            num_predict=Settings.MAX_TOKENS
        )
    
    @staticmethod
    def get_available_models():
        """Get list of available models for comparison"""
        return Settings.LLM_MODELS
