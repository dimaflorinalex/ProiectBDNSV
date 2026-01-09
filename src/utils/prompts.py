class PromptTemplates:
    """Prompt templates for different tasks"""
    
    SQL_GENERATION_PROMPT = """You are a SQL expert. Given a database schema and a natural language question, generate a valid SQL query.

Database Schema:
{schema}

Question: {question}

Important rules:
- Return ONLY the SQL query, nothing else
- Use proper SQL syntax for SQLite
- Match table and column names exactly as shown in the schema
- Use appropriate JOINs when needed
- Add WHERE clauses for filtering
- Use GROUP BY for aggregations
- Return SELECT statements only

SQL Query:"""

    CLARIFICATION_PROMPT = """The following question might be ambiguous: "{question}"

Database Schema:
{schema}

Analyze if this question is ambiguous given the schema. If it is ambiguous, provide 2-3 possible interpretations.
If it's clear, respond with "CLEAR"."""

    SUMMARIZATION_PROMPT = """Given a SQL query and its results, provide a natural language summary.

Question: {question}
SQL Query: {sql_query}
Results: {results}

Provide a clear, concise summary of the results in natural language that directly answers the original question."""

    ERROR_CORRECTION_PROMPT = """The following SQL query has an error:

SQL Query: {sql_query}
Error: {error}

Database Schema:
{schema}

Generate a corrected SQL query that fixes this error. Return ONLY the corrected SQL query, nothing else."""

    FEW_SHOT_PROMPT = """You are a SQL expert. Here are some examples:

Example 1:
Question: How many customers are there?
Schema: CREATE TABLE customers (id INTEGER, name TEXT, email TEXT);
SQL: SELECT COUNT(*) FROM customers;

Example 2:
Question: What are the top 5 products by price?
Schema: CREATE TABLE products (id INTEGER, name TEXT, price REAL);
SQL: SELECT name, price FROM products ORDER BY price DESC LIMIT 5;

Example 3:
Question: Show employees and their departments
Schema: CREATE TABLE employees (id INTEGER, name TEXT, department_id INTEGER); CREATE TABLE departments (id INTEGER, name TEXT);
SQL: SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id;

Now generate SQL for:
Schema: {schema}
Question: {question}

SQL Query:"""

    CHAIN_OF_THOUGHT_PROMPT = """You are a SQL expert. Let's think step by step.

Database Schema:
{schema}

Question: {question}

First, let's break down what we need to do:
1. Identify which tables are needed
2. Determine what columns to select
3. Decide if JOINs are needed
4. Consider any filters (WHERE clauses)
5. Think about aggregations or sorting

Now generate the SQL query. Return ONLY the final SQL query."""

    FEEDBACK_ENHANCED_PROMPT = """You are a SQL expert. Learn from previous successful queries and common mistakes.

Database Schema:
{schema}

{feedback_examples}

{feedback_corrections}

Question: {question}

Generate a SQL query following best practices from the examples above. Return ONLY the SQL query."""
