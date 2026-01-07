# Sample test queries for the Text-To-SQL application

SAMPLE_QUERIES = [
    {
        "question": "How many employees are there?",
        "expected_tables": ["employees"],
        "expected_keywords": ["COUNT", "SELECT"]
    },
    {
        "question": "Show me all departments",
        "expected_tables": ["departments"],
        "expected_keywords": ["SELECT", "FROM", "departments"]
    },
    {
        "question": "What is the average salary?",
        "expected_tables": ["employees"],
        "expected_keywords": ["AVG", "salary"]
    },
    {
        "question": "List employees with their departments",
        "expected_tables": ["employees", "departments"],
        "expected_keywords": ["JOIN"]
    },
    {
        "question": "Who are the top 5 highest paid employees?",
        "expected_tables": ["employees"],
        "expected_keywords": ["ORDER BY", "DESC", "LIMIT"]
    },
    {
        "question": "How many employees in each department?",
        "expected_tables": ["employees", "departments"],
        "expected_keywords": ["GROUP BY", "COUNT"]
    },
    {
        "question": "Show all active projects",
        "expected_tables": ["projects"],
        "expected_keywords": ["WHERE", "status", "active"]
    },
    {
        "question": "What is the total budget of all departments?",
        "expected_tables": ["departments"],
        "expected_keywords": ["SUM", "budget"]
    }
]
