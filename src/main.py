#!/usr/bin/env python3
"""
Text-To-SQL Application
Main entry point for CLI and Web interfaces
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import argparse
import sys
from src.interfaces.cli import CLI
from src.interfaces.web import WebInterface
from src.llm.llm_comparator import LLMComparator
from config.settings import Settings

def main():
    parser = argparse.ArgumentParser(
        description="Text-To-SQL Application using Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run interactive CLI
  python src/main.py --mode cli
  
  # Run web interface
  python src/main.py --mode web
  
  # Run single query
  python src/main.py --mode cli --question "How many employees are there?"
  
  # Compare models
  python src/main.py --mode compare --question "Show all departments"
  
  # Use specific model
  python src/main.py --mode cli --model mistral:7b
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["cli", "web", "compare"],
        default="cli",
        help="Interface mode: cli (command-line), web (Gradio), or compare (model comparison)"
    )
    
    parser.add_argument(
        "--question",
        type=str,
        help="Single question to process (only for CLI mode)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=Settings.DEFAULT_MODEL,
        help=f"LLM model to use (default: {Settings.DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create public link for web interface (only for web mode)"
    )
    
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to database file"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "web":
            print("🌐 Starting web interface...")
            print(f"📦 Using model: {args.model}")
            print(f"🔗 Opening at http://localhost:{Settings.WEB_PORT}")
            
            interface = WebInterface(model_name=args.model)
            interface.launch(share=args.share)
            
        elif args.mode == "compare":
            if not args.question:
                print("❌ Error: --question is required for compare mode")
                sys.exit(1)
            
            print("🔄 Comparing models...")
            print(f"Question: {args.question}\n")
            
            from src.chain.text_to_sql_chain import TextToSQLChain
            chain = TextToSQLChain(db_path=args.db_path)
            
            comparator = LLMComparator()
            results = comparator.compare_models(args.question, chain.schema)
            
            print("=" * 70)
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
            chain.close()
            
        else:  # CLI mode
            cli = CLI(model_name=args.model)
            
            try:
                if args.question:
                    # Run single query
                    cli.run_single_query(args.question)
                else:
                    # Run interactive mode
                    cli.interactive_mode()
            finally:
                cli.close()
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
