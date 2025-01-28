import json
from typing import Dict, List
from collections import defaultdict


def analyze_final_results(file_path: str = "model_responses.json"):
    # Load results
    with open(file_path, 'r') as f:
        results = json.load(f)

    # Initialize tracking variables
    total_wins = defaultdict(int)
    total_votes = defaultdict(int)
    average_rankings = defaultdict(list)

    # Analyze each question
    for question_result in results:
        # Track wins
        winners = question_result["analysis"]["winners"]
        for winner in winners:
            total_wins[winner] += 1

        # Track votes
        votes = question_result["analysis"]["total_votes_received"]
        for model, vote_count in votes.items():
            total_votes[model] += vote_count

        # Track rankings
        rankings = question_result["analysis"]["average_rankings"]
        for model, rank in rankings.items():
            average_rankings[model].append(rank)

    # Calculate final averages
    final_rankings = {
        model: sum(ranks) / len(ranks)
        for model, ranks in average_rankings.items()
    }

    # Prepare final summary
    summary = {
        "total_questions": len(results),
        "model_performance": {
            model: {
                "total_wins": total_wins[model],
                "total_votes": total_votes[model],
                "average_ranking": final_rankings[model]
            }
            for model in total_wins.keys()
        }
    }

    # Determine overall winner(s)
    max_wins = max(total_wins.values())
    winners = [
        model for model, wins in total_wins.items()
        if wins == max_wins
    ]

    summary["overall_winners"] = winners

    return summary


if __name__ == "__main__":
    # Analyze results
    results = analyze_final_results()
    print(results)