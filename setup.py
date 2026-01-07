from setuptools import setup, find_packages

setup(
    name="text-to-sql-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.38",
        "sqlalchemy>=2.0.25",
        "ollama>=0.1.6",
        "gradio>=4.16.0",
        "pandas>=2.1.4",
        "sqlparse>=0.4.4",
        "datasets>=2.16.1",
    ],
    python_requires=">=3.8",
    author="Text-To-SQL Team",
    description="Text-To-SQL application using Ollama and LangChain",
)
