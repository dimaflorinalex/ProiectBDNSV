from typing import List, Dict, Optional
from src.handlers.feedback_handler import FeedbackHandler

class FeedbackLearningSystem:
    """
    Use historical feedback to improve query generation
    Implements a closed feedback loop by incorporating user feedback into prompts
    """
    
    def __init__(self, feedback_handler: FeedbackHandler = None):
        self.feedback_handler = feedback_handler or FeedbackHandler()
    
    def build_learned_examples(self, question: str, max_examples: int = 3) -> str:
        """
        Build few-shot examples from positive feedback
        
        Args:
            question: Current question to find similar examples
            max_examples: Maximum number of examples to include
            
        Returns:
            Formatted examples string for prompt
        """
        # First try to get similar queries
        similar = self.feedback_handler.get_similar_queries(question, limit=max_examples)
        
        # If not enough similar, get general positive examples
        if len(similar) < max_examples:
            needed = max_examples - len(similar)
            positive = self.feedback_handler.get_positive_examples(limit=needed)
            examples = similar + positive
        else:
            examples = similar[:max_examples]
        
        if not examples:
            return ""
        
        examples_text = "Here are some examples of good queries from previous interactions:\n\n"
        
        for idx, example in enumerate(examples, 1):
            examples_text += f"Example {idx}:\n"
            examples_text += f"Question: {example['question']}\n"
            examples_text += f"SQL: {example['sql_query']}\n\n"
        
        return examples_text
    
    def build_correction_guidance(self, max_corrections: int = 2) -> str:
        """
        Build guidance from user corrections
        
        Args:
            max_corrections: Maximum number of corrections to include
            
        Returns:
            Formatted correction guidance for prompt
        """
        corrections = self.feedback_handler.get_corrected_examples(limit=max_corrections)
        
        if not corrections:
            return ""
        
        guidance_text = "Learn from these common mistakes:\n\n"
        
        for idx, correction in enumerate(corrections, 1):
            guidance_text += f"Mistake {idx}:\n"
            guidance_text += f"Question: {correction['question']}\n"
            guidance_text += f"Wrong: {correction['original_query']}\n"
            guidance_text += f"Correct: {correction['corrected_query']}\n\n"
        
        return guidance_text
    
    def enhance_prompt_with_feedback(self, base_prompt: str, question: str, 
                                    use_examples: bool = True, 
                                    use_corrections: bool = True) -> str:
        """
        Enhance a base prompt with learned feedback
        
        Args:
            base_prompt: Original prompt template
            question: Current question
            use_examples: Include positive examples
            use_corrections: Include correction guidance
            
        Returns:
            Enhanced prompt with feedback
        """
        enhancements = []
        
        if use_examples:
            examples = self.build_learned_examples(question, max_examples=3)
            if examples:
                enhancements.append(examples)
        
        if use_corrections:
            corrections = self.build_correction_guidance(max_corrections=2)
            if corrections:
                enhancements.append(corrections)
        
        if not enhancements:
            return base_prompt
        
        # Insert enhancements before the actual question
        enhanced = base_prompt.replace(
            "Question:", 
            "\n".join(enhancements) + "Now generate SQL for this question:\n\nQuestion:"
        )
        
        return enhanced
    
    def get_learning_status(self) -> Dict:
        """
        Get status of feedback learning system
        
        Returns:
            Dictionary with learning system statistics
        """
        stats = self.feedback_handler.get_feedback_stats()
        positive_examples = len(self.feedback_handler.get_positive_examples(limit=100))
        corrections = len(self.feedback_handler.get_corrected_examples(limit=100))
        has_data = self.feedback_handler.has_learning_data()
        
        return {
            "has_learning_data": has_data,
            "positive_examples": positive_examples,
            "corrections": corrections,
            "total_feedback": stats['total_feedback'],
            "average_rating": stats['average_rating']
        }
    
    def suggest_improvement_areas(self) -> List[str]:
        """
        Suggest areas where more feedback would help
        
        Returns:
            List of suggestions
        """
        suggestions = []
        status = self.get_learning_status()
        
        if status['positive_examples'] < 5:
            suggestions.append("Collect more positive examples (current: {})".format(
                status['positive_examples']))
        
        if status['corrections'] == 0:
            suggestions.append("No corrections recorded. Provide corrected queries for failed attempts.")
        
        if status['total_feedback'] < 10:
            suggestions.append("Limited feedback data. Rate more queries to improve learning.")
        
        if status['average_rating'] < 3.5:
            suggestions.append("Low average rating ({:.1f}). System needs improvement.".format(
                status['average_rating']))
        
        if not suggestions:
            suggestions.append("Feedback system is working well! Continue providing feedback.")
        
        return suggestions
