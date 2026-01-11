# Benchmarks

This directory contains benchmark evaluations for the Text-to-SQL system using standard datasets.

## Spider Benchmark

Spider is a large-scale cross-domain semantic parsing and text-to-SQL dataset. It tests the system's ability to generate SQL queries across various database schemas.

**Dataset Location:** `data/benchmarks/spider/`

**Usage:**
```bash
# Run with default settings (10 samples)
python benchmarks/spider_benchmark.py

# Run with custom number of samples
python benchmarks/spider_benchmark.py --samples 20

# Run with specific model
python benchmarks/spider_benchmark.py --model mistral --samples 15
```

## Metrics

The benchmark evaluates two key metrics:

1. **Exact Match (EM)**: Percentage of generated SQL queries that exactly match the gold standard queries (after normalization)
2. **Execution Accuracy (EX)**: Percentage of generated queries that produce the same results as the gold standard queries

**Note:** Execution accuracy is generally more important as there are often multiple valid ways to write the same SQL query.

## Command-Line Arguments

The benchmark script supports the following arguments:

- `--samples`: Number of samples to evaluate (default: 10)
- `--model`: LLM model to use for generation (default: llama3)
  - Options: `llama3`, `mistral`, `codellama`

## Example Output

```
======================================================================
SPIDER BENCHMARK EVALUATION
======================================================================

Evaluating 5 samples...

[1/5] DB: concert_singer
  Q: How many singers do we have?...
  ❌ No exact match
  ✅ Execution match
[2/5] DB: concert_singer
  Q: What is the total number of singers?...
  ❌ No exact match
  ✅ Execution match
...

======================================================================
RESULTS
======================================================================
Total Samples: 5
Exact Match Accuracy: 0.00%
Execution Accuracy: 100.00%
======================================================================
```

## Dataset Structure

```
data/benchmarks/spider/
├── dev.json                    # Development set questions
└── spider_data/
    └── spider_data/
        └── database/           # Database files (.sqlite)
            ├── concert_singer/
            ├── car_1/
            └── ...
```

## Implementation Details

### Database Connection
Each example in the benchmark uses the specific database referenced in the question. The benchmark automatically:
1. Loads the appropriate database for each question
2. Generates SQL using the TextToSQLChain
3. Executes both generated and gold queries
4. Compares results

### Error Handling
- Missing databases are skipped with warnings
- SQL generation failures are tracked separately
- Execution errors are caught and reported

### Performance Notes
- Larger sample sizes will take longer to evaluate
- LLM response time affects total benchmark duration

## Extending the Benchmark

To add a new benchmark:

1. Create a new benchmark class inheriting common structure
2. Implement `load_dataset()`, `normalize_sql()`, `exact_match()`, `execution_match()`
3. Add database path configuration
4. Implement `run_benchmark()` method with appropriate evaluation logic

## Troubleshooting

### "Database not found" errors
Ensure the dataset is properly extracted in the `data/benchmarks/spider/` directory.

### Timeout errors
Try reducing the number of samples in the code.

## References

- **Spider**: [https://yale-lily.github.io/spider](https://yale-lily.github.io/spider)
