# Quick Start Guide

## Prerequisites

1. **Install Ollama** from https://ollama.ai
2. **Pull required models**:
   ```bash
   ollama pull llama3:latest
   ollama pull mistral:7b
   ollama pull codellama:latest
   ```
3. **Make sure Ollama is running** (it should start automatically)

## Installation

```bash
# Navigate to project directory
cd ProiectBDNSV

# Install dependencies
pip install -r requirements.txt
```

## Quick Test

Run the basic tests:
```bash
python tests/test_basic.py
```

## Usage

### 1. CLI Interface (Interactive)

```bash
python src/main.py --mode cli
```

Commands in CLI:
- Type your question to generate SQL
- Type `compare` to compare models
- Type `stats` to see feedback statistics
- Type `learning` to see learning system status
- Type `quit` or `exit` to quit

### 2. CLI Interface (Single Query)

```bash
python src/main.py --mode cli --question "How many employees are there?"
```

### 3. Web Interface

```bash
python src/main.py --mode web
```

Then open http://localhost:7860 in your browser.

### 4. Compare Models

```bash
python src/main.py --mode compare --question "Show all departments"
```

## Example Questions

Try these questions:
- "How many employees are there?"
- "Show me all departments"
- "What is the average salary?"
- "List employees with their departments"
- "Who are the top 5 highest paid employees?"
- "How many employees in each department?"
- "Show all active projects"
- "What is the total budget of all departments?"

## Running Benchmarks

```bash
python benchmarks/spider_benchmark.py
```

Note: You need to download the Spider dataset separately.

## Project Structure

- `src/main.py` - Main entry point
- `src/chain/` - LangChain pipelines (text-to-sql, summarization)
- `src/llm/` - LLM management (factory, comparator)
- `src/query/` - SQL processing (generator, executor, validator)
- `src/handlers/` - Special handlers (ambiguity, feedback)
- `src/database/` - Database operations
- `src/interfaces/` - User interfaces (CLI, Web)
- `config/` - Configuration settings
- `benchmarks/` - Benchmark tests
- `tests/` - Unit tests

## Troubleshooting

### Ollama Connection Error
- Make sure Ollama is running: `ollama serve`
- Check if models are available: `ollama list`

### Model Not Found
- Pull the model: `ollama pull llama3:latest`

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt`

## Features Implemented

✅ Natural language to SQL conversion
✅ Multi-LLM comparison (llama3, mistral, codellama)
✅ Error detection and automatic correction
✅ Closed feedback loop with learning system
  - Rate queries (1-5 scale)
  - Provide corrected SQL queries
  - System learns from positive examples
  - Learns from user corrections
  - Automatic prompt enhancement
✅ Ambiguity detection and clarification
✅ Result summarization in natural language
✅ Few-shot prompting
✅ Chain-of-thought prompting
✅ CLI interface with feedback collection
✅ Web interface (Gradio) with correction input
✅ Spider benchmark support
✅ Complete test suite
✅ Learning status monitoring

