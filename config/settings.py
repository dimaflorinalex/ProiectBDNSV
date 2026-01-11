import os
from typing import List

class Settings:
    """Application settings and configuration"""
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # LLM Models to compare
    LLM_MODELS: List[str] = [
        "llama3:latest",
        "mistral:7b",
        "codellama:latest"
    ]
    
    # Default model
    DEFAULT_MODEL = "llama3:latest"
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/sample_database.db")
    
    # Temperature for generation (0.0 = deterministic, 1.0 = creative)
    TEMPERATURE = 0.1
    
    # Max tokens for generation
    MAX_TOKENS = 2000
    
    # Feedback storage
    FEEDBACK_DB_PATH = "data/feedback.db"
    
    # Benchmark paths
    SPIDER_DATA_PATH = "data/benchmarks/spider"
    
    # Maximum retries for SQL generation
    MAX_RETRIES = 2
    
    # Web interface settings
    WEB_PORT = 7860
    WEB_SHARE = False  # Set to True to create public link

settings = Settings()
