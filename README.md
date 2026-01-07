# Proiect BDNSV

## Team members:
- Dima Florin-Alexandru - Grupa 462 - FMI Unibuc
- Copilot

## Text-To-SQL Application with Ollama

A complete Text-To-SQL solution using LangChain and Ollama for local LLM execution.

## Features

- **Natural Language to SQL**: Convert natural language questions to SQL queries
- **Multiple LLM Support**: Compare results across different Ollama models (llama3, mistral, codellama)
- **Error Handling**: Automatic detection and correction of invalid SQL
- **User Feedback Loop**: Thumbs up/down feedback mechanism
- **Ambiguity Detection**: Handle unclear questions with clarification prompts
- **Result Summarization**: Convert SQL results back to natural language
- **Benchmark Testing**: Evaluate accuracy using Spider and Bird benchmarks
- **Dual Interface**: Both CLI and Web UI (Gradio) interfaces

## Prerequisites

1. **Install Ollama**: Download from [https://ollama.ai](https://ollama.ai)
2. **Pull required models**:
   ```bash
   ollama pull llama3:latest
   ollama pull mistral:7b
   ollama pull codellama:latest
   ```

## Installation

```bash
# Clone the repository
cd ProiectBDNSV

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Usage

### CLI Interface

```bash
python src/main.py --mode cli
```

### Web Interface

```bash
python src/main.py --mode web
```

The web interface will open at `http://localhost:7860`

### Compare Models

```bash
python src/main.py --mode compare --question "Show all employees"
```

### Run Benchmarks

```bash
python benchmarks/spider_benchmark.py
```

## Project Structure

```
ProiectBDNSV/
├── src/
│   ├── main.py                 # Entry point
│   ├── chain/                  # LangChain pipelines
│   │   ├── text_to_sql_chain.py
│   │   └── summarization_chain.py
│   ├── llm/                    # LLM management
│   │   ├── llm_factory.py
│   │   └── llm_comparator.py
│   ├── query/                  # SQL processing
│   │   ├── generator.py
│   │   ├── executor.py
│   │   └── validator.py
│   ├── handlers/               # Special handlers
│   │   ├── ambiguity_handler.py
│   │   └── feedback_handler.py
│   ├── database/               # Database operations
│   │   └── connection.py
│   ├── interfaces/             # User interfaces
│   │   ├── cli.py
│   │   └── web.py
│   └── utils/                  # Utilities
│       └── prompts.py
├── config/
│   └── settings.py             # Configuration
├── benchmarks/                 # Benchmark tests
│   ├── spider_benchmark.py
│   └── bird_benchmark.py
├── tests/                      # Unit tests
├── data/                       # Sample database
└── requirements.txt
```

## Configuration

Edit `config/settings.py` to change:
- Ollama base URL
- Available models
- Database path
- Temperature and other LLM parameters

## Example Questions

- "How many employees are there?"
- "Show the top 5 highest paid employees"
- "What is the average salary by department?"
- "List all projects in the Engineering department"

## License

MIT License
