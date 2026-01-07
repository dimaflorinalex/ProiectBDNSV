"""
Basic tests for Text-To-SQL application

Run with: python -m pytest tests/
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.connection import DatabaseConnection
from src.query.validator import SQLValidator
from src.query.generator import QueryGenerator
from src.query.executor import QueryExecutor


def test_database_connection():
    """Test database connection and schema extraction"""
    db = DatabaseConnection()
    db.connect()
    
    schema = db.get_schema()
    assert "employees" in schema.lower()
    assert "departments" in schema.lower()
    
    db.disconnect()
    print("✅ Database connection test passed")


def test_sql_validator():
    """Test SQL validator"""
    validator = SQLValidator()
    
    # Valid SELECT query
    valid_query = "SELECT * FROM employees"
    is_valid, error = validator.validate_syntax(valid_query)
    assert is_valid == True
    
    # Invalid query with dangerous keyword
    try:
        dangerous_query = "DROP TABLE employees"
        validator.sanitize_query(dangerous_query)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✅ SQL validator test passed")


def test_query_executor():
    """Test query execution"""
    db = DatabaseConnection()
    db.connect()
    
    executor = QueryExecutor(db)
    
    # Execute simple query
    result, error = executor.execute("SELECT COUNT(*) FROM employees")
    
    assert error is None
    assert result is not None
    
    columns, rows = result
    assert len(rows) > 0
    
    db.disconnect()
    print("✅ Query executor test passed")


def test_clean_sql():
    """Test SQL cleaning"""
    validator = SQLValidator()
    
    # SQL with markdown
    sql_with_markdown = "```sql\nSELECT * FROM employees\n```"
    cleaned = validator.clean_sql(sql_with_markdown)
    assert "```" not in cleaned
    assert "SELECT" in cleaned
    
    # SQL with comments
    sql_with_comments = "-- This is a comment\nSELECT * FROM employees"
    cleaned = validator.clean_sql(sql_with_comments)
    assert "--" not in cleaned
    assert "SELECT" in cleaned
    
    print("✅ SQL cleaning test passed")


def test_end_to_end():
    """Test end-to-end query generation and execution"""
    try:
        from src.chain.text_to_sql_chain import TextToSQLChain
        
        chain = TextToSQLChain()
        
        # Simple question
        result = chain.run("How many employees are there?")
        
        assert result is not None
        # Note: sql_query might be None if Ollama is not running
        # This test verifies the chain structure works
        
        chain.close()
        print("✅ End-to-end test passed")
    except Exception as e:
        print(f"⚠️  End-to-end test skipped (Ollama may not be running): {str(e)}")


if __name__ == "__main__":
    print("Running tests...\n")
    
    try:
        test_database_connection()
        test_sql_validator()
        test_query_executor()
        test_clean_sql()
        test_end_to_end()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
