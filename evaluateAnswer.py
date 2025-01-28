import json
import os
from typing import Dict, List, Any
from datetime import datetime


class AnswerEvaluator:
    RESULTS_FILE = os.path.join(os.getcwd(), "model_responses.json")
    print(RESULTS_FILE)
    @staticmethod
    def load_existing_results() -> List[Dict[str, Any]]:
        """Load existing results from JSON file."""
        try:
            if os.path.exists(AnswerEvaluator.RESULTS_FILE):
                with open(AnswerEvaluator.RESULTS_FILE, 'r') as f:
                    data = json.load(f)
                    # Validate it's a list
                    if not isinstance(data, list):
                        return []
                    return data
            return []
        except Exception as e:
            print(f"Error loading existing results: {str(e)}")
            return []

    @staticmethod
    def save_results(results: List[Dict[str, Any]]):
        """Save results to JSON file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(AnswerEvaluator.RESULTS_FILE), exist_ok=True)

            with open(AnswerEvaluator.RESULTS_FILE, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            print(f"Error saving results: {str(e)}")

    @staticmethod
    def determine_winners(votes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Determine winners based on votes and rankings."""
        vote_counts = {}
        rankings = {}

        try:
            # Count votes and collect rankings
            for voter, vote_data in votes.items():
                if "votes" in vote_data and isinstance(vote_data["votes"], list):
                    for voted_model in vote_data["votes"]:
                        vote_counts[voted_model] = vote_counts.get(voted_model, 0) + 1

                if "ranking" in vote_data and isinstance(vote_data["ranking"], dict):
                    for model, rank in vote_data["ranking"].items():
                        if model not in rankings:
                            rankings[model] = []
                        rankings[model].append(rank)

            # Calculate average ranking for each model
            avg_rankings = {
                model: sum(ranks) / len(ranks)
                for model, ranks in rankings.items()
                if ranks  # Only if there are ranks
            }

            return {
                "vote_counts": vote_counts,
                "average_rankings": avg_rankings,
                "winners": [
                    model for model, count in vote_counts.items()
                    if count == max(vote_counts.values(), default=0)
                ]
            }
        except Exception as e:
            print(f"Error determining winners: {str(e)}")
            return {
                "vote_counts": {},
                "average_rankings": {},
                "winners": []
            }

    @staticmethod
    def format_results(query_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format the results for storage and display."""
        try:
            winners_data = AnswerEvaluator.determine_winners(query_result.get("votes", {}))

            formatted_result = {
                "timestamp": datetime.now().isoformat(),
                "query": query_result.get("query", ""),
                "answers": query_result.get("answers", {}),
                "voting_results": {
                    model: {
                        "votes_given": vote_data.get("votes", []),
                        "rankings_given": vote_data.get("ranking", {}),
                        "reasoning": vote_data.get("reasoning", {})
                    }
                    for model, vote_data in query_result.get("votes", {}).items()
                },
                "analysis": {
                    "total_votes_received": winners_data["vote_counts"],
                    "average_rankings": winners_data["average_rankings"],
                    "winners": winners_data["winners"]
                }
            }

            # Load existing results and append new result
            all_results = AnswerEvaluator.load_existing_results()
            all_results.append(formatted_result)
            AnswerEvaluator.save_results(all_results)

            return formatted_result

        except Exception as e:
            error_result = {
                "error": f"Error formatting results: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "query": query_result.get("query", ""),
                "raw_data": query_result
            }
            return error_result