from openai import OpenAI
import os
import json
from typing import Dict, List, Tuple, Any


class ModelHandler:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.models = {
            "GPT-4": "gpt-4",
            "GPT-4o": "gpt-4",
            "GPT-4o-mini": "gpt-4",
            "GPT3.5": "gpt-3.5-turbo"
        }

    def get_answer(self, model_name: str, query: str) -> str:
        """Get response from a specific model for a given query."""
        try:
            response = self.client.chat.completions.create(
                model=self.models[model_name],
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Provide clear, concise answers."},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting response from {model_name}: {str(e)}"

    def clean_json_string(self, json_str: str) -> str:
        """Clean up JSON string by removing comments and markdown."""
        lines = json_str.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove comments
            if '//' in line:
                line = line[:line.index('//')]
            cleaned_lines.append(line)

        result = '\n'.join(cleaned_lines)

        # Remove markdown if present
        if result.startswith('```json'):
            result = result[7:]
        if result.endswith('```'):
            result = result[:-3]

        return result.strip()

    def get_vote(self, model_name: str, answers: Dict[str, str], query: str) -> Dict[str, Any]:
        """Get a model's votes and reasoning for other models' answers."""
        voting_prompt = f"""
        Original question: {query}

        Here are answers from different models (excluding yours):
        {'\n'.join([f'{model}: {answer}' for model, answer in answers.items()])}

        Please evaluate all answers and provide your votes. You can vote for multiple answers if they are equally good.

        Return your response in this exact JSON format, no markdown or comments:
        {{
            "votes": ["model1", "model2"],
            "ranking": {{
                "model1": 1,
                "model2": 1,
                "model3": 2
            }},
            "reasoning": {{
                "model1": "explanation1",
                "model2": "explanation2",
                "model3": "explanation3"
            }}
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.models[model_name],
                messages=[
                    {
                        "role": "system",
                        "content": "You are an evaluator. Return only valid JSON with no comments or markdown."
                    },
                    {"role": "user", "content": voting_prompt}
                ]
            )

            # Get and clean the response
            result = response.choices[0].message.content
            cleaned_result = self.clean_json_string(result)

            # Parse and validate JSON
            parsed_result = json.loads(cleaned_result)

            # Validate required keys
            required_keys = ["votes", "ranking", "reasoning"]
            if not all(key in parsed_result for key in required_keys):
                raise ValueError("Missing required keys in response")

            return parsed_result

        except Exception as e:
            return {
                "votes": [],
                "ranking": {},
                "reasoning": {},
                "error": f"Error getting vote from {model_name}: {str(e)}"
            }