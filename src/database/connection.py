import sqlite3
import os
from typing import List, Tuple, Optional, Dict, Any
from config.settings import Settings

class DatabaseConnection:
    """Manage database connections and operations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Settings.DATABASE_PATH
        self.connection = None
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure database file exists, create sample if not"""
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self._create_sample_database()
    
    def _create_sample_database(self):
        """Create a sample database for testing"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        # Create sample tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department_id INTEGER,
                salary REAL,
                hire_date TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                budget REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department_id INTEGER,
                start_date TEXT,
                end_date TEXT,
                status TEXT
            )
        """)
        
        # Insert sample data
        cursor.execute("INSERT INTO departments VALUES (1, 'Engineering', 500000)")
        cursor.execute("INSERT INTO departments VALUES (2, 'Sales', 300000)")
        cursor.execute("INSERT INTO departments VALUES (3, 'HR', 200000)")
        cursor.execute("INSERT INTO departments VALUES (4, 'Marketing', 250000)")
        
        cursor.execute("INSERT INTO employees VALUES (1, 'John Doe', 1, 75000, '2020-01-15')")
        cursor.execute("INSERT INTO employees VALUES (2, 'Jane Smith', 1, 85000, '2019-03-20')")
        cursor.execute("INSERT INTO employees VALUES (3, 'Bob Johnson', 2, 65000, '2021-06-10')")
        cursor.execute("INSERT INTO employees VALUES (4, 'Alice Williams', 3, 60000, '2020-11-05')")
        cursor.execute("INSERT INTO employees VALUES (5, 'Charlie Brown', 1, 95000, '2018-07-12')")
        cursor.execute("INSERT INTO employees VALUES (6, 'Diana Prince', 2, 70000, '2021-02-18')")
        cursor.execute("INSERT INTO employees VALUES (7, 'Eve Davis', 4, 68000, '2020-09-22')")
        
        cursor.execute("INSERT INTO projects VALUES (1, 'Website Redesign', 1, '2023-01-01', '2023-06-30', 'completed')")
        cursor.execute("INSERT INTO projects VALUES (2, 'Sales Campaign', 2, '2023-03-01', '2023-12-31', 'active')")
        cursor.execute("INSERT INTO projects VALUES (3, 'Employee Training', 3, '2023-05-15', '2023-11-30', 'active')")
        cursor.execute("INSERT INTO projects VALUES (4, 'Mobile App', 1, '2024-01-01', '2024-12-31', 'active')")
        
        conn.commit()
        conn.close()
    
    def connect(self):
        """Create database connection"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str) -> Tuple[Optional[Tuple[List, List]], Optional[str]]:
        """
        Execute a SQL query and return results
        
        Returns:
            Tuple of ((columns, rows), error)
        """
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Convert Row objects to lists
            rows = [list(row) for row in results]
            
            return (columns, rows), None
        except Exception as e:
            return None, str(e)
    
    def get_schema(self) -> str:
        """Get database schema as text"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cursor.fetchall()
            
            schema_text = "Database Schema:\n\n"
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                schema_text += f"Table: {table_name}\n"
                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    pk = " (PRIMARY KEY)" if col[5] else ""
                    schema_text += f"  - {col_name} {col_type}{pk}\n"
                schema_text += "\n"
            
            return schema_text
        except Exception as e:
            return f"Error getting schema: {str(e)}"
    
    def get_schema_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get database schema as dictionary"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cursor.fetchall()
            
            schema_dict = {}
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                schema_dict[table_name] = [
                    {
                        "name": col[1],
                        "type": col[2],
                        "nullable": not col[3],
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ]
            
            return schema_dict
        except Exception as e:
            return {"error": str(e)}
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
