import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from config.settings import Settings
import os

class FeedbackHandler:
    """Handle user feedback for query improvement"""
    
    def __init__(self, feedback_db_path: str = None):
        self.db_path = feedback_db_path or Settings.FEEDBACK_DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize feedback database"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                sql_query TEXT NOT NULL,
                rating INTEGER,
                comment TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id INTEGER,
                original_query TEXT NOT NULL,
                corrected_query TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (feedback_id) REFERENCES feedback (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_feedback(self, question: str, sql_query: str, rating: int, 
                     comment: str = None) -> int:
        """
        Add user feedback
        
        Args:
            question: Natural language question
            sql_query: Generated SQL query
            rating: Rating (1=thumbs down, 5=thumbs up)
            comment: Optional comment
            
        Returns:
            Feedback ID
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO feedback (question, sql_query, rating, comment, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (question, sql_query, rating, comment, timestamp))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def add_correction(self, feedback_id: int, original_query: str, 
                       corrected_query: str):
        """
        Add corrected query
        
        Args:
            feedback_id: ID of the feedback entry
            original_query: Original generated query
            corrected_query: User-corrected query
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO corrections (feedback_id, original_query, corrected_query, timestamp)
            VALUES (?, ?, ?, ?)
        """, (feedback_id, original_query, corrected_query, timestamp))
        
        conn.commit()
        conn.close()
    
    def get_feedback_stats(self) -> Dict:
        """
        Get feedback statistics
        
        Returns:
            Dictionary with feedback statistics
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(rating) FROM feedback")
        avg_rating = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating >= 4")
        positive_feedback = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM corrections")
        total_corrections = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_feedback": total_feedback,
            "average_rating": round(avg_rating, 2),
            "positive_feedback": positive_feedback,
            "total_corrections": total_corrections
        }
    
    def get_low_rated_queries(self, limit: int = 10) -> List[Dict]:
        """
        Get queries with low ratings for improvement
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of low-rated queries
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT question, sql_query, rating, comment, timestamp
            FROM feedback
            WHERE rating <= 2
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_corrections(self, limit: int = 10) -> List[Dict]:
        """
        Get user corrections for learning
        
        Args:
            limit: Maximum number of corrections to return
            
        Returns:
            List of corrections
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.original_query, c.corrected_query, c.timestamp,
                   f.question
            FROM corrections c
            JOIN feedback f ON c.feedback_id = f.id
            ORDER BY c.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_positive_examples(self, limit: int = 5) -> List[Dict]:
        """
        Get highly-rated queries as positive examples for few-shot learning
        
        Args:
            limit: Maximum number of examples to return
            
        Returns:
            List of positive examples with question and SQL
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT question, sql_query, rating
            FROM feedback
            WHERE rating >= 4
            ORDER BY rating DESC, timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_similar_queries(self, question: str, limit: int = 3) -> List[Dict]:
        """
        Get similar queries based on keywords (simple matching)
        
        Args:
            question: Current question
            limit: Maximum number of similar queries
            
        Returns:
            List of similar queries with high ratings
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Extract keywords (simple approach - split and lowercase)
        keywords = [word.lower() for word in question.split() if len(word) > 3]
        
        if not keywords:
            return []
        
        # Build query with LIKE clauses
        like_clauses = " OR ".join(["LOWER(question) LIKE ?" for _ in keywords])
        query = f"""
            SELECT question, sql_query, rating
            FROM feedback
            WHERE rating >= 4 AND ({like_clauses})
            ORDER BY rating DESC
            LIMIT ?
        """
        
        params = [f"%{kw}%" for kw in keywords] + [limit]
        cursor.execute(query, params)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_corrected_examples(self, limit: int = 5) -> List[Dict]:
        """
        Get user-corrected queries to learn from mistakes
        
        Args:
            limit: Maximum number of corrections to return
            
        Returns:
            List of corrections with original and corrected queries
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.question, c.original_query, c.corrected_query, c.timestamp
            FROM corrections c
            JOIN feedback f ON c.feedback_id = f.id
            ORDER BY c.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def has_learning_data(self) -> bool:
        """
        Check if there's enough feedback data for learning
        
        Returns:
            True if there's useful feedback data
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating >= 4")
        positive_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM corrections")
        correction_count = cursor.fetchone()[0]
        
        conn.close()
        
        return positive_count >= 3 or correction_count >= 1
