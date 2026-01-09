import gradio as gr
from src.chain.text_to_sql_chain import TextToSQLChain
from src.handlers.ambiguity_handler import AmbiguityHandler
from src.handlers.feedback_handler import FeedbackHandler
from src.handlers.feedback_learning import FeedbackLearningSystem
from src.llm.llm_comparator import LLMComparator
from config.settings import Settings
import pandas as pd

class WebInterface:
    """Gradio web interface for Text-To-SQL"""
    
    def __init__(self, model_name: str = None):
        self.chain = TextToSQLChain(model_name=model_name)
        self.ambiguity_handler = AmbiguityHandler(model_name)
        self.feedback_handler = FeedbackHandler()
        self.learning_system = FeedbackLearningSystem(self.feedback_handler)
        self.comparator = LLMComparator()
    
    def process_question(self, question: str, use_few_shot: bool, use_cot: bool):
        """Process a natural language question"""
        if not question:
            return "Please enter a question.", "", "", None
        
        try:
            # Run the chain
            result = self.chain.run(
                question, 
                use_few_shot=use_few_shot,
                use_chain_of_thought=use_cot
            )
            
            if result["error"]:
                error_msg = f"❌ Error: {result['error']}\n\n"
                error_msg += "Attempts:\n"
                for attempt in result["attempts"]:
                    error_msg += f"\nAttempt {attempt['attempt']}:\n"
                    if attempt['query']:
                        error_msg += f"  Query: {attempt['query']}\n"
                    if attempt['error']:
                        error_msg += f"  Error: {attempt['error']}\n"
                return error_msg, "", "", None
            
            sql_query = result["sql_query"]
            summary = result["summary"]
            
            # Format results as DataFrame
            if result["results"]:
                columns = result["results"]["columns"]
                rows = result["results"]["rows"]
                df = pd.DataFrame(rows, columns=columns)
            else:
                df = None
            
            return sql_query, summary, "", df
            
        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", None
    
    def submit_feedback(self, question: str, sql_query: str, rating: int, comment: str, corrected_query: str):
        """Submit user feedback with optional correction"""
        if not question or not sql_query:
            return "⚠️ No query to provide feedback on."
        
        try:
            feedback_id = self.feedback_handler.add_feedback(question, sql_query, rating, comment)
            
            # If correction provided, save it
            if corrected_query and corrected_query.strip() and rating <= 2:
                self.feedback_handler.add_correction(feedback_id, sql_query, corrected_query.strip())
                return "✅ Thank you for your feedback and correction! This will help improve future queries."
            
            return "✅ Thank you for your feedback!"
        except Exception as e:
            return f"❌ Error submitting feedback: {str(e)}"
    
    def compare_models(self, question: str):
        """Compare different LLM models"""
        if not question:
            return "Please enter a question."
        
        try:
            results = self.comparator.compare_models(question, self.chain.schema)
            
            comparison_text = "# Model Comparison Results\n\n"
            
            for model, result in results.items():
                comparison_text += f"## {model}\n"
                comparison_text += f"- **Execution Time:** {result['execution_time']:.2f}s\n"
                
                if result['success']:
                    comparison_text += f"- **Status:** ✅ Success\n"
                    comparison_text += f"- **Query:** `{result['query']}`\n"
                else:
                    comparison_text += f"- **Status:** ❌ Failed\n"
                    comparison_text += f"- **Error:** {result.get('error', 'Unknown')}\n"
                
                comparison_text += "\n"
            
            return comparison_text
            
        except Exception as e:
            return f"❌ Error comparing models: {str(e)}"
    
    def get_feedback_stats(self):
        """Get feedback statistics"""
        try:
            stats = self.feedback_handler.get_feedback_stats()
            
            stats_text = "# Feedback Statistics\n\n"
            stats_text += f"- **Total Feedback:** {stats['total_feedback']}\n"
            stats_text += f"- **Average Rating:** {stats['average_rating']}/5\n"
            stats_text += f"- **Positive Feedback:** {stats['positive_feedback']}\n"
            stats_text += f"- **Total Corrections:** {stats['total_corrections']}\n"
            
            return stats_text
        except Exception as e:
            return f"❌ Error getting stats: {str(e)}"
    
    def get_learning_status(self):
        """Get learning system status"""
        try:
            status = self.learning_system.get_learning_status()
            
            status_text = "# Learning System Status\n\n"
            status_text += f"- **Learning Data Available:** {'Yes ✅' if status['has_learning_data'] else 'No ❌'}\n"
            status_text += f"- **Positive Examples:** {status['positive_examples']}\n"
            status_text += f"- **Corrections:** {status['corrections']}\n"
            status_text += f"- **Total Feedback:** {status['total_feedback']}\n"
            status_text += f"- **Average Rating:** {status['average_rating']}/5\n\n"
            
            status_text += "## Improvement Suggestions\n\n"
            for suggestion in self.learning_system.suggest_improvement_areas():
                status_text += f"- {suggestion}\n"
            
            return status_text
        except Exception as e:
            return f"❌ Error getting learning status: {str(e)}"
    
    def get_schema_info(self):
        """Get database schema information"""
        return self.chain.schema
    
    def launch(self, share: bool = False):
        """Launch Gradio interface"""
        
        with gr.Blocks(title="Text-To-SQL with Ollama") as demo:
            gr.Markdown("# 🤖 Text-To-SQL Application")
            gr.Markdown("Convert natural language questions to SQL queries using local Ollama LLMs")
            
            with gr.Tab("Query Generator"):
                with gr.Row():
                    with gr.Column(scale=2):
                        question_input = gr.Textbox(
                            label="Your Question",
                            placeholder="e.g., How many employees are in each department?",
                            lines=2
                        )
                        
                        with gr.Row():
                            few_shot_checkbox = gr.Checkbox(label="Use Few-Shot Prompting", value=False)
                            cot_checkbox = gr.Checkbox(label="Use Chain-of-Thought", value=False)
                        
                        submit_btn = gr.Button("Generate SQL", variant="primary")
                    
                    with gr.Column(scale=1):
                        schema_display = gr.Textbox(
                            label="Database Schema",
                            value=self.get_schema_info(),
                            lines=15,
                            interactive=False
                        )
                
                sql_output = gr.Textbox(label="Generated SQL Query", lines=3)
                summary_output = gr.Textbox(label="Summary", lines=3)
                results_output = gr.Dataframe(label="Query Results")
                
                gr.Markdown("### Provide Feedback")
                with gr.Row():
                    rating_slider = gr.Slider(
                        minimum=1, maximum=5, step=1, value=3,
                        label="Rating (1=Bad, 5=Excellent)"
                    )
                    comment_input = gr.Textbox(label="Comment (Optional)", placeholder="Any comments?")
                
                corrected_query_input = gr.Textbox(
                    label="Corrected SQL Query (Optional - provide if rating ≤ 2)",
                    placeholder="If the query was wrong, provide the correct SQL here...",
                    lines=2
                )
                
                feedback_btn = gr.Button("Submit Feedback")
                feedback_output = gr.Textbox(label="Feedback Status")
                
                submit_btn.click(
                    fn=self.process_question,
                    inputs=[question_input, few_shot_checkbox, cot_checkbox],
                    outputs=[sql_output, summary_output, feedback_output, results_output]
                )
                
                feedback_btn.click(
                    fn=self.submit_feedback,
                    inputs=[question_input, sql_output, rating_slider, comment_input, corrected_query_input],
                    outputs=feedback_output
                )
            
            with gr.Tab("Model Comparison"):
                gr.Markdown("### Compare Different LLM Models")
                gr.Markdown("See how different models generate SQL for the same question")
                
                compare_question = gr.Textbox(
                    label="Question",
                    placeholder="Enter a question to compare across models",
                    lines=2
                )
                compare_btn = gr.Button("Compare Models", variant="primary")
                compare_output = gr.Markdown(label="Comparison Results")
                
                compare_btn.click(
                    fn=self.compare_models,
                    inputs=compare_question,
                    outputs=compare_output
                )
            
            with gr.Tab("Statistics"):
                gr.Markdown("### Feedback Statistics")
                
                stats_btn = gr.Button("Refresh Statistics", variant="primary")
                stats_output = gr.Markdown(value=self.get_feedback_stats())
                
                stats_btn.click(
                    fn=self.get_feedback_stats,
                    inputs=[],
                    outputs=stats_output
                )
            
            with gr.Tab("Learning System"):
                gr.Markdown("### Feedback Learning System")
                gr.Markdown("The system learns from your feedback to improve query generation over time.")
                
                learning_btn = gr.Button("Refresh Learning Status", variant="primary")
                learning_output = gr.Markdown(value=self.get_learning_status())
                
                learning_btn.click(
                    fn=self.get_learning_status,
                    inputs=[],
                    outputs=learning_output
                )
            
            with gr.Tab("About"):
                gr.Markdown("""
                ## About This Application
                
                This Text-To-SQL application uses **Ollama** for local LLM execution, ensuring:
                - 🔒 **Privacy**: All processing happens locally
                - 🚀 **Speed**: No API latency
                - 💰 **Cost**: Completely free to use
                
                ### Features
                - Natural language to SQL query generation
                - Multiple LLM model comparison
                - Error detection and correction
                - User feedback loop
                - Few-shot and chain-of-thought prompting
                
                ### Models Used
                - llama3:latest
                - mistral:7b
                - codellama:latest
                
                ### Requirements
                Make sure Ollama is running and the models are pulled:
                ```bash
                ollama pull llama3:latest
                ollama pull mistral:7b
                ollama pull codellama:latest
                ```
                """)
        
        demo.launch(
            server_port=Settings.WEB_PORT,
            share=share,
            server_name="0.0.0.0",
            theme=gr.themes.Soft()
        )

if __name__ == "__main__":
    interface = WebInterface()
    interface.launch()
