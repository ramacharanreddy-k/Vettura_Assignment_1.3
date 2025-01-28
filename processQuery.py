import json
from typing import Dict, Any
from openLLM import ModelHandler


class QueryProcessor:
    def __init__(self, model_handler: ModelHandler):
        self.model_handler = model_handler
        self.models = ["GPT-4", "GPT-4o", "GPT-4o-mini", "GPT3.5"]

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query through all models and collect their answers and votes."""
        # Get answers from all models
        answers = {}
        for model in self.models:
            answers[model] = self.model_handler.get_answer(model, query)

        # Get votes from each model
        votes = {}
        for model in self.models:
            # Create dict of other models' answers (excluding current model)
            other_answers = {k: v for k, v in answers.items() if k != model}

            # Get vote data (now returns a complete dictionary)
            vote_data = self.model_handler.get_vote(model, other_answers, query)
            votes[model] = vote_data

        # Return structured results
        return {
            "query": query,
            "answers": answers,
            "votes": votes
        }