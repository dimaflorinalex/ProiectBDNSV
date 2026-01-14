import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import os
from typing import List, Dict
from src.chain.text_to_sql_chain import TextToSQLChain
from src.database.connection import DatabaseConnection
import time

class SpiderBenchmark:
    """
    Benchmark using Spider dataset
    
    Spider is a large-scale complex and cross-domain semantic parsing and 
    text-to-SQL dataset.
    
    Note: You need to download the Spider dataset separately from:
    https://yale-lily.github.io/spider
    """
    
    def __init__(self, data_path: str = "data/benchmarks/spider", model_name: str = None):
        self.data_path = data_path
        self.model_name = model_name
        self.results = []
        self.db_base_path = os.path.join(data_path, "spider_data", "spider_data", "database")
    
    def load_dataset(self, split: str = "dev") -> List[Dict]:
        """
        Load Spider dataset
        
        Args:
            split: 'train' or 'dev'
            
        Returns:
            List of examples
        """
        json_path = os.path.join(self.data_path, f"{split}.json")
        
        if not os.path.exists(json_path):
            print(f"⚠️ Spider dataset not found at {json_path}")
            print("Please download from: https://yale-lily.github.io/spider")
            return []
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return data
    
    def normalize_sql(self, sql: str) -> str:
        """
        Normalize SQL for comparison by removing irrelevant differences
        while preserving semantic meaning
        """
        import re
        
        # Convert to uppercase
        sql = sql.upper()
        
        # Remove comments
        sql = re.sub(r'--[^\n]*', '', sql)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Remove trailing semicolons
        sql = sql.rstrip(';').strip()
        
        # Normalize whitespace (including newlines and tabs)
        sql = ' '.join(sql.split())
        
        # Remove AS keyword for aliases
        sql = re.sub(r'\bAS\s+', '', sql)
        
        # Remove table prefixes from columns (e.g., "s.Name" -> "Name", "T1.id" -> "id")
        sql = re.sub(r'\b[A-Z]\d*\.', '', sql)  # Matches s., t1., T2., etc.
        
        # Normalize COUNT(*) 
        sql = re.sub(r'COUNT\s*\(\s*\*\s*\)', 'COUNT(*)', sql)
        
        # DON'T remove spaces around operators yet - we need them for alias detection
        # Just normalize multiple spaces to single space
        sql = ' '.join(sql.split())
        
        return sql.strip()
    
    def remove_aliases(self, sql: str) -> str:
        """
        Remove column and table aliases from normalized SQL
        """
        import re
        
        # Remove column aliases in SELECT clause
        # Work with the SELECT clause between SELECT and FROM
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql)
        if select_match:
            select_clause = select_match.group(1)
            
            # Remove aliases after functions: "FUNCTION(...) ALIAS" -> "FUNCTION(...)"
            # This handles COUNT(*) TOTAL, AVG(AGE) AVG_AGE, etc.
            select_clause = re.sub(r'\)\s+[A-Z_0-9]+(?=\s*(,|$))', ')', select_clause)
            
            # Also handle simple column aliases: "COLUMN_NAME ALIAS" -> "COLUMN_NAME"
            # But be careful not to remove function names
            select_clause = re.sub(r'\b([A-Z_0-9]+)\s+[A-Z_0-9]+(?=\s*(,|$))(?!\()', r'\1', select_clause)
            
            sql = sql.replace(select_match.group(1), select_clause)
        
        # Remove table aliases (FROM table alias -> FROM table)
        sql = re.sub(r'(FROM|JOIN)\s+([A-Z_]+)\s+[A-Z]\d*\b', r'\1 \2', sql)
        
        # Now normalize spacing around operators for final comparison
        sql = re.sub(r'\s*\(\s*', ' (', sql)
        sql = re.sub(r'\s*\)\s*', ') ', sql)
        sql = re.sub(r'\s*,\s*', ', ', sql)
        sql = re.sub(r'\s*=\s*', ' = ', sql)
        sql = re.sub(r'\s*<\s*', ' < ', sql)
        sql = re.sub(r'\s*>\s*', ' > ', sql)
        
        # Normalize spaces
        sql = ' '.join(sql.split())
        
        return sql
    
    def exact_match(self, predicted: str, gold: str) -> bool:
        """
        Check if predicted SQL matches gold SQL after normalization.
        This checks structural equivalence, not just string equality.
        """
        pred_norm = self.normalize_sql(predicted)
        gold_norm = self.normalize_sql(gold)
        
        # Direct match after normalization
        if pred_norm == gold_norm:
            return True
        
        # Try with alias removal
        pred_no_aliases = self.remove_aliases(pred_norm)
        gold_no_aliases = self.remove_aliases(gold_norm)
        
        return pred_no_aliases == gold_no_aliases
    
    def execution_match(self, predicted: str, gold: str, db_path: str) -> bool:
        """Check if predicted SQL produces same results as gold SQL"""
        try:
            # Create connection to specific database
            db_conn = DatabaseConnection(db_path)
            db_conn.connect()
            
            pred_result, pred_error = db_conn.execute_query(predicted)
            gold_result, gold_error = db_conn.execute_query(gold)
            
            db_conn.disconnect()
            
            if pred_error or gold_error:
                return False
            
            # Compare results
            pred_cols, pred_rows = pred_result
            gold_cols, gold_rows = gold_result
            
            # Sort rows for comparison
            pred_rows_sorted = sorted([tuple(row) for row in pred_rows])
            gold_rows_sorted = sorted([tuple(row) for row in gold_rows])
            
            return pred_rows_sorted == gold_rows_sorted
            
        except Exception as e:
            print(f"    Execution error: {str(e)}")
            return False
    
    def run_benchmark(self, max_samples: int = 10) -> Dict:
        """
        Run benchmark evaluation
        
        Args:
            max_samples: Maximum number of samples to evaluate (for testing)
            
        Returns:
            Dictionary with evaluation metrics
        """
        print("=" * 70)
        print("SPIDER BENCHMARK EVALUATION")
        print("=" * 70)
        
        dataset = self.load_dataset("dev")
        
        if not dataset:
            return {
                "error": "Dataset not found",
                "exact_match_accuracy": 0,
                "execution_accuracy": 0,
                "total_samples": 0
            }
        
        # Limit samples for testing
        dataset = dataset[:max_samples]
        
        exact_matches = 0
        execution_matches = 0
        total = len(dataset)
        
        print(f"\nEvaluating {total} samples...\n")
        
        for idx, example in enumerate(dataset):
            question = example.get("question", "")
            gold_sql = example.get("query", "")
            db_id = example.get("db_id", "")
            
            # Get database path
            db_path = os.path.join(self.db_base_path, db_id, f"{db_id}.sqlite")
            
            print(f"[{idx+1}/{total}] DB: {db_id}")
            print(f"  Q: {question[:70]}...")
            
            # Check if database exists
            if not os.path.exists(db_path):
                print(f"  ⚠️ Database not found: {db_path}")
                continue
            
            try:
                # Use the specific database for this example
                chain = TextToSQLChain(db_path=db_path, model_name=self.model_name)
                result = chain.run(question)
                
                if result["sql_query"]:
                    predicted_sql = result["sql_query"]
                    
                    # Exact match
                    if self.exact_match(predicted_sql, gold_sql):
                        exact_matches += 1
                        print("  ✅ Exact match")
                        print(f"    Query: {predicted_sql[:100]}...")
                    else:
                        print("  ❌ No exact match")
                        print(f"    Predicted: {predicted_sql[:100]}...")
                        print(f"    Gold: {gold_sql[:100]}...")
                    
                    # Execution match
                    if self.execution_match(predicted_sql, gold_sql, db_path):
                        execution_matches += 1
                        print("  ✅ Execution match")
                    else:
                        print("  ❌ No execution match")
                else:
                    print("  ❌ Failed to generate SQL")
                
                chain.close()
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
            
            time.sleep(0.5)  # Rate limiting
        
        exact_match_acc = (exact_matches / total) * 100 if total > 0 else 0
        execution_acc = (execution_matches / total) * 100 if total > 0 else 0
        
        results = {
            "exact_match_accuracy": exact_match_acc,
            "execution_accuracy": execution_acc,
            "exact_matches": exact_matches,
            "execution_matches": execution_matches,
            "total_samples": total,
            "model": self.model_name or "default"
        }
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Total Samples: {total}")
        print(f"Exact Match Accuracy: {exact_match_acc:.2f}%")
        print(f"Execution Accuracy: {execution_acc:.2f}%")
        print("=" * 70)
        
        return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Spider benchmark evaluation')
    parser.add_argument('--samples', type=int, default=10, help='Number of samples to evaluate (default: 10)')
    parser.add_argument('--model', type=str, default=None, help='Model name to use (default: llama3)')
    
    args = parser.parse_args()
    
    benchmark = SpiderBenchmark(model_name=args.model)
    results = benchmark.run_benchmark(max_samples=args.samples)
