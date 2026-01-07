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

class BirdBenchmark:
    """
    Benchmark using BIRD dataset
    
    BIRD (BIg Bench for LaRge-scale Database Grounded Text-to-SQL Evaluation)
    is a challenging benchmark for text-to-SQL with large databases.
    
    Note: You need to download the BIRD dataset separately from:
    https://bird-bench.github.io/
    """
    
    def __init__(self, data_path: str = "data/benchmarks/bird", model_name: str = None):
        self.data_path = data_path
        self.model_name = model_name
        self.results = []
    
    def load_dataset(self, split: str = "dev") -> List[Dict]:
        """
        Load BIRD dataset
        
        Args:
            split: 'train' or 'dev'
            
        Returns:
            List of examples
        """
        json_path = os.path.join(self.data_path, f"{split}.json")
        
        if not os.path.exists(json_path):
            print(f"⚠️ BIRD dataset not found at {json_path}")
            print("Please download from: https://bird-bench.github.io/")
            return []
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return data
    
    def normalize_sql(self, sql: str) -> str:
        """Normalize SQL for comparison"""
        sql = sql.upper()
        sql = ' '.join(sql.split())
        return sql
    
    def exact_match(self, predicted: str, gold: str) -> bool:
        """Check if predicted SQL exactly matches gold SQL"""
        return self.normalize_sql(predicted) == self.normalize_sql(gold)
    
    def execution_match(self, predicted: str, gold: str, db_connection: DatabaseConnection) -> bool:
        """Check if predicted SQL produces same results as gold SQL"""
        try:
            pred_result, pred_error = db_connection.execute_query(predicted)
            gold_result, gold_error = db_connection.execute_query(gold)
            
            if pred_error or gold_error:
                return False
            
            pred_cols, pred_rows = pred_result
            gold_cols, gold_rows = gold_result
            
            pred_rows_sorted = sorted([tuple(row) for row in pred_rows])
            gold_rows_sorted = sorted([tuple(row) for row in gold_rows])
            
            return pred_rows_sorted == gold_rows_sorted
            
        except Exception:
            return False
    
    def calculate_difficulty_scores(self, results_by_difficulty: Dict) -> Dict:
        """Calculate scores broken down by difficulty level"""
        scores = {}
        
        for difficulty, metrics in results_by_difficulty.items():
            if metrics['total'] > 0:
                scores[difficulty] = {
                    'exact_match': (metrics['exact_match'] / metrics['total']) * 100,
                    'execution': (metrics['execution'] / metrics['total']) * 100,
                    'total': metrics['total']
                }
        
        return scores
    
    def run_benchmark(self, max_samples: int = 10) -> Dict:
        """
        Run benchmark evaluation
        
        Args:
            max_samples: Maximum number of samples to evaluate
            
        Returns:
            Dictionary with evaluation metrics
        """
        print("=" * 70)
        print("BIRD BENCHMARK EVALUATION")
        print("=" * 70)
        
        dataset = self.load_dataset("dev")
        
        if not dataset:
            return {
                "error": "Dataset not found",
                "exact_match_accuracy": 0,
                "execution_accuracy": 0,
                "total_samples": 0
            }
        
        dataset = dataset[:max_samples]
        
        exact_matches = 0
        execution_matches = 0
        total = len(dataset)
        
        # Track by difficulty if available
        difficulty_results = {
            'simple': {'exact_match': 0, 'execution': 0, 'total': 0},
            'moderate': {'exact_match': 0, 'execution': 0, 'total': 0},
            'challenging': {'exact_match': 0, 'execution': 0, 'total': 0}
        }
        
        print(f"\nEvaluating {total} samples...\n")
        
        for idx, example in enumerate(dataset):
            question = example.get("question", "")
            gold_sql = example.get("SQL", "") or example.get("query", "")
            db_id = example.get("db_id", "")
            difficulty = example.get("difficulty", "moderate").lower()
            
            print(f"[{idx+1}/{total}] [{difficulty}] {question[:50]}...")
            
            try:
                chain = TextToSQLChain(model_name=self.model_name)
                result = chain.run(question)
                
                if result["sql_query"]:
                    predicted_sql = result["sql_query"]
                    
                    # Track difficulty
                    if difficulty in difficulty_results:
                        difficulty_results[difficulty]['total'] += 1
                    
                    # Exact match
                    if self.exact_match(predicted_sql, gold_sql):
                        exact_matches += 1
                        if difficulty in difficulty_results:
                            difficulty_results[difficulty]['exact_match'] += 1
                        print("  ✅ Exact match")
                    else:
                        print("  ❌ No exact match")
                    
                    # Execution match
                    if self.execution_match(predicted_sql, gold_sql, chain.db):
                        execution_matches += 1
                        if difficulty in difficulty_results:
                            difficulty_results[difficulty]['execution'] += 1
                        print("  ✅ Execution match")
                    else:
                        print("  ❌ No execution match")
                else:
                    print("  ❌ Failed to generate SQL")
                    if difficulty in difficulty_results:
                        difficulty_results[difficulty]['total'] += 1
                
                chain.close()
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
            
            time.sleep(0.5)
        
        exact_match_acc = (exact_matches / total) * 100 if total > 0 else 0
        execution_acc = (execution_matches / total) * 100 if total > 0 else 0
        
        difficulty_scores = self.calculate_difficulty_scores(difficulty_results)
        
        results = {
            "exact_match_accuracy": exact_match_acc,
            "execution_accuracy": execution_acc,
            "exact_matches": exact_matches,
            "execution_matches": execution_matches,
            "total_samples": total,
            "model": self.model_name or "default",
            "difficulty_breakdown": difficulty_scores
        }
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Total Samples: {total}")
        print(f"Exact Match Accuracy: {exact_match_acc:.2f}%")
        print(f"Execution Accuracy: {execution_acc:.2f}%")
        
        if difficulty_scores:
            print("\nBy Difficulty:")
            for difficulty, scores in difficulty_scores.items():
                print(f"  {difficulty.capitalize()}: EM={scores['exact_match']:.1f}%, EX={scores['execution']:.1f}% (n={scores['total']})")
        
        print("=" * 70)
        
        return results

if __name__ == "__main__":
    benchmark = BirdBenchmark()
    results = benchmark.run_benchmark(max_samples=5)
