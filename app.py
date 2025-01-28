import gradio as gr
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from openLLM import ModelHandler
from processQuery import QueryProcessor
from evaluateAnswer import AnswerEvaluator

# Load environment variables
load_dotenv()

# Predefined questions
QUESTIONS = [
    "How many 'r' characters are present in the word 'strawberry'?",
    "What is the result of 135 × 27 + 896 ÷ 4?",
    "If all roses are flowers and some flowers are red, can we say all roses are red?",
    "A car travels 40 miles per hour for the first 3 hours, then 50 miles per hour for the next 2 hours, and finally 60 miles per hour for the last 1 hour. What is the car's average speed?",
    "I have cities, but no houses; I have forests, but no trees; I have rivers, but no water. What am I?"
]


class GradioInterface:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Please set OPENAI_API_KEY in your .env file")

        self.model_handler = ModelHandler(api_key)
        self.query_processor = QueryProcessor(self.model_handler)
        self.evaluator = AnswerEvaluator()

    def format_output(self, results: Dict[str, Any]) -> str:
        """Format results for nice display in Gradio."""
        return json.dumps(results, indent=2)

    def process_and_evaluate(self, question: str) -> str:
        """Process the selected question and get results from all models."""
        try:
            # Process query and evaluate results
            result = self.query_processor.process_query(question)
            formatted_results = self.evaluator.format_results(result)

            # Return formatted results as a nicely formatted string
            return self.format_output(formatted_results)
        except Exception as e:
            return json.dumps({
                "error": f"An error occurred: {str(e)}",
                "query": question
            }, indent=2)

    def create_interface(self):
        interface = gr.Interface(
            fn=self.process_and_evaluate,
            inputs=gr.Dropdown(
                choices=QUESTIONS,
                label="Select a Question",
                value=QUESTIONS[0]  # Set default value to first question
            ),
            outputs=gr.Code(
                label="Results",
                language="json"
            ),
            title="Model Comparison Interface",
            description="Select a question to see how different models answer and evaluate each other. Results are stored in model_responses.json"
        )
        return interface


def main():
    app = GradioInterface()
    interface = app.create_interface()
    # Launch with a larger height and share enabled
    interface.launch(height=800, share=True)


if __name__ == "__main__":
    main()