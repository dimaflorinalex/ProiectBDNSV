import sys
from typing import Optional
from src.chain.text_to_sql_chain import TextToSQLChain
from src.handlers.ambiguity_handler import AmbiguityHandler
from src.handlers.feedback_handler import FeedbackHandler
from src.handlers.feedback_learning import FeedbackLearningSystem
from src.llm.llm_comparator import LLMComparator

class CLI:
    """Command-line interface for Text-To-SQL"""
    
    def __init__(self, model_name: str = None):
        self.chain = TextToSQLChain(model_name=model_name)
        self.ambiguity_handler = AmbiguityHandler(model_name)
        self.feedback_handler = FeedbackHandler()
        self.learning_system = FeedbackLearningSystem(self.feedback_handler)
        self.comparator = LLMComparator()
    
    def print_header(self):
        """Print CLI header"""
        print("=" * 70)
        print(" " * 20 + "TEXT-TO-SQL APPLICATION")
        print(" " * 15 + "Using Ollama for Local LLM Execution")
        print("=" * 70)
        print()
    
    def print_result(self, result: dict):
        """Print query result"""
        print("\n" + "=" * 70)
        
        if result["error"]:
            print(f"❌ Error: {result['error']}")
            print("\nAttempts made:")
            for attempt in result["attempts"]:
                print(f"\nAttempt {attempt['attempt']}:")
                if attempt['query']:
                    print(f"  Query: {attempt['query']}")
                if attempt['error']:
                    print(f"  Error: {attempt['error']}")
        else:
            print(f"✅ SQL Query Generated:")
            print(f"   {result['sql_query']}")
            print()
            
            if result["results"]:
                columns = result["results"]["columns"]
                rows = result["results"]["rows"]
                
                print(f"📊 Results ({len(rows)} row(s)):")
                print()
                
                # Print table header
                print("   " + " | ".join(str(col) for col in columns))
                print("   " + "-" * (len(" | ".join(str(col) for col in columns))))
                
                # Print rows (limit to 10)
                for row in rows[:10]:
                    print("   " + " | ".join(str(val) if val is not None else "NULL" for val in row))
                
                if len(rows) > 10:
                    print(f"\n   ... and {len(rows) - 10} more rows")
            
            print()
            print(f"💬 Summary:")
            print(f"   {result['summary']}")
        
        print("=" * 70)
    
    def get_feedback(self, question: str, sql_query: str) -> Optional[int]:
        """Get user feedback on query"""
        print("\n📝 Was this result helpful?")
        print("   1 - Thumbs down (not helpful)")
        print("   5 - Thumbs up (very helpful)")
        print("   s - Skip feedback")
        
        feedback = input("\nYour rating (1-5 or s): ").strip().lower()
        
        if feedback == 's':
            return None
        
        try:
            rating = int(feedback)
            if 1 <= rating <= 5:
                comment = input("Optional comment: ").strip() or None
                feedback_id = self.feedback_handler.add_feedback(question, sql_query, rating, comment)
                print("✅ Thank you for your feedback!")
                
                # If low rating, offer to provide correction
                if rating <= 2:
                    print("\n🔧 Would you like to provide a corrected SQL query?")
                    provide_correction = input("   (y/n): ").strip().lower()
                    
                    if provide_correction == 'y':
                        print("\n   Enter the correct SQL query (or press Enter to skip):")
                        corrected_query = input("   SQL> ").strip()
                        
                        if corrected_query:
                            self.feedback_handler.add_correction(feedback_id, sql_query, corrected_query)
                            print("✅ Correction saved! This will help improve future queries.")
                
                return rating
            else:
                print("Invalid rating. Skipping feedback.")
                return None
        except ValueError:
            print("Invalid input. Skipping feedback.")
            return None
    
    def compare_models_mode(self):
        """Compare different models"""
        print("\n🔄 MODEL COMPARISON MODE")
        print("-" * 70)
        
        question = input("\nEnter your question: ").strip()
        if not question:
            print("No question provided.")
            return
        
        print("\nComparing models...")
        results = self.comparator.compare_models(question, self.chain.schema)
        
        print("\n" + "=" * 70)
        print("COMPARISON RESULTS")
        print("=" * 70)
        
        for model, result in results.items():
            print(f"\n📦 Model: {model}")
            print(f"   Time: {result['execution_time']:.2f}s")
            
            if result['success']:
                print(f"   ✅ Query: {result['query']}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        print("=" * 70)
    
    def interactive_mode(self):
        """Run interactive CLI mode"""
        self.print_header()
        
        print("Commands:")
        print("  - Type your question to generate SQL")
        print("  - Type 'compare' to compare models")
        print("  - Type 'stats' to see feedback statistics")
        print("  - Type 'learning' to see learning system status")
        print("  - Type 'quit' or 'exit' to quit")
        print()
        
        # Show learning status if data is available
        if self.learning_system.feedback_handler.has_learning_data():
            print("✨ Feedback learning is enabled! Using learned examples to improve queries.\n")
        
        while True:
            try:
                question = input("\n💭 Your question: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if question.lower() == 'compare':
                    self.compare_models_mode()
                    continue
                
                if question.lower() == 'stats':
                    stats = self.feedback_handler.get_feedback_stats()
                    print("\n📊 FEEDBACK STATISTICS")
                    print("-" * 70)
                    print(f"   Total Feedback: {stats['total_feedback']}")
                    print(f"   Average Rating: {stats['average_rating']}/5")
                    print(f"   Positive Feedback: {stats['positive_feedback']}")
                    print(f"   Total Corrections: {stats['total_corrections']}")
                    print("-" * 70)
                    continue
                
                if question.lower() == 'learning':
                    status = self.learning_system.get_learning_status()
                    print("\n🎓 LEARNING SYSTEM STATUS")
                    print("-" * 70)
                    print(f"   Learning Data Available: {'Yes ✅' if status['has_learning_data'] else 'No ❌'}")
                    print(f"   Positive Examples: {status['positive_examples']}")
                    print(f"   Corrections: {status['corrections']}")
                    print(f"   Total Feedback: {status['total_feedback']}")
                    print(f"   Average Rating: {status['average_rating']}/5")
                    print("\n   Improvement Suggestions:")
                    for suggestion in self.learning_system.suggest_improvement_areas():
                        print(f"   • {suggestion}")
                    print("-" * 70)
                    continue
                
                # Check for ambiguity
                print("\n🔍 Analyzing question...")
                is_ambiguous = self.ambiguity_handler.detect_ambiguity(question, self.chain.schema)
                
                if is_ambiguous:
                    print("\n⚠️  This question might be ambiguous.")
                    clarification = self.ambiguity_handler.clarify(question, self.chain.schema)
                    print(f"\n{clarification}")
                    
                    proceed = input("\nProceed anyway? (y/n): ").strip().lower()
                    if proceed != 'y':
                        continue
                
                # Generate and execute query
                print("\n⚙️  Generating SQL query...")
                result = self.chain.run(question)
                
                self.print_result(result)
                
                # Get feedback if successful
                if result["sql_query"] and not result["error"]:
                    self.get_feedback(question, result["sql_query"])
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    def run_single_query(self, question: str):
        """Run a single query (non-interactive)"""
        self.print_header()
        print(f"Question: {question}\n")
        
        result = self.chain.run(question)
        self.print_result(result)
    
    def close(self):
        """Clean up resources"""
        self.chain.close()

if __name__ == "__main__":
    cli = CLI()
    try:
        if len(sys.argv) > 1:
            # Run single query from command line
            question = " ".join(sys.argv[1:])
            cli.run_single_query(question)
        else:
            # Run interactive mode
            cli.interactive_mode()
    finally:
        cli.close()
