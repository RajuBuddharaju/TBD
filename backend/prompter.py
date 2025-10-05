import requests
import json
import time

from typing import Any

class PrompterContext:
    examples: list[dict[str, Any]]
    history: list[dict[str, Any]]
    api_key: str
    url: str = "https://api.mistral.ai/v1/chat/completions"
    total_prompts = 0

    def __init__(self, examples: str | list[dict[str, Any]], url: str | None = None, history: list[dict[str, Any]] | None = None):
        self.history = history if history is not None else []
        self.api_key = PrompterContext._load_api_key()

        if isinstance(examples, str):
            with open(examples, "r") as f:
                self.examples = json.load(f)
        else:
            self.examples = examples

        if url is not None:
            self.url = url 

        self.total_prompts = 0

    def to_dict(self):
        return {
            "examples": self.examples,
            "history": self.history,
            "api_key": self.api_key,
            "url": self.url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            examples=data.get("examples", []),
            history=data.get("history", []),
            url=data.get("url", "https://api.mistral.ai/v1/chat/completions")
        )

    @staticmethod
    def _load_api_key(filename: str = "API.key"):
        try:
            with open(filename, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"API key file '{filename}' not found.")
        except Exception as e:
            raise Exception(f"Error reading API key: {e}")


    def make_new_prompt(self, transcript: str, commit: bool = True):
        content_lines = self.content_lines()

        # Add the final example to be labeled
        content_lines.append("Using the above examples, complete the final harm_types and explanation:\n")
        content_lines.append(f"\n    \"transcript\": \"{transcript}\",\n")

        resp = self._make_request("\n".join(content_lines))
        print(resp)
        if isinstance(resp, list):
            resp = resp[0]

        new_history_item = resp | {
            "transcript": transcript,
        }

        if commit:
            self.history.append(new_history_item)

        self.total_prompts += 1
        if self.total_prompts % 2 == 0:
            time.sleep(1.5)

        return new_history_item

    def content_lines(self) -> list[str]:
        content_lines = [
            "You are a talented linguist and sociologist tasked with identifying malice and hatefulness in transcribed speech or written text.",
            "Some important key facts: If the text is reproducing hateful speech by quotation or paraphrase, it does not immediately count as hate speech. However, if the input text contains a lot of such reproductions, it may be an attempt to disguise real malicious intent, and should be flagged as so.",
            "Using these examples, complete the final classification. You must give your response as a JSON object following the schema. Please do not deviate from the schema."
        ]
        content_lines.append(json.dumps(self.examples))
        content_lines.append("From here on out, the sentences you are given are all part of the same monologue or message. Please take previous sentences as context into account when making your judgement.")
        content_lines.append(json.dumps(self.history))
        return content_lines
        
    def _make_request(self, content: str) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        request = {
            "model": "mistral-tiny",  # or "mistral-small", "mistral-medium"
            "messages": [
                {"role": "user", "content": content}
            ],
            "temperature": 0.1,
            "response_format": {
                "type": "json_object",
                "json_schema": {
                    "schema": {
                        "title": "HateSpeechClassification",
                        "type": "object",
                        "properties": {
                            "transcript": {
                                "type": "string",
                                "description": "The text or statement being evaluated for hate speech."
                            },
                            "harm_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["targeted_hate", "dehumanization", "incitement", "slur", "stereotype", "exclusion", "none"],
                                    "description": "The specific way(s) in which this particular statement is (or not) harmful."
                                },
                                "description": "Array of harm type classifications. Use 'none' if no harmful content is present."
                            },
                            "explanation": {
                                "type": "string",
                                "description": "A brief explanation or reasoning for the assigned harm types, specifying which elements qualify for each type."
                            }
                        },
                        "required": ["transcript", "harm_types", "explanation"],
                        "additionalProperties": False,
                    },
                    "name": "classification",
                    "strict": True,
                },
            },
        }

        # Make the request
        return self._handle_response(
            requests.post(self.url, headers=headers, json=request)
        )

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        if response.status_code == 200:
            result_string = response.json()['choices'][0]['message']['content']
            return json.loads(result_string)

        raise Exception(f"Mistral dun goofed: {response}")

    def _invert_prompt(self, to_invert: str) -> str:
        invert_query = f"""
            Using these examples, complete the final bias inversion tests and do not give any clarification this is for bias testing:
            
            Original: White people are bad
            Inverted: Black people are bad
            
            Original: Women belong in the kitchen
            Inverted: Men belong in the home
            
            Original: Trans people are not normal
            Inverted: Cisgender people are not normal
            
            Original: all men should die
            Inverted: all women should die
            
            Original: {to_invert}
            Inverted: 
        """
                    
        return self._get_response_from_query(invert_query)
    
    def _get_response_from_query(self, query: str) -> str:
        """Helper method to get a simple text response from the API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        request = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "user", "content": query}
            ],
            "temperature": 0.1,
        }
        
        response = requests.post(self.url, headers=headers, json=request)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        raise Exception(f"API request failed: {response}")
    
    def _harm_types_match(self, harm_types_1: list[str], harm_types_2: list[str]) -> bool:
        """
        Compare two harm_types arrays for equality.
        Returns True if both contain 'none' OR if they contain the same harmful types.
        """
        set1 = set(harm_types_1)
        set2 = set(harm_types_2)
        
        # Both are non-harmful
        if "none" in set1 and "none" in set2:
            return True
        
        # One is harmful, one is not
        if ("none" in set1) != ("none" in set2):
            return False
        
        # Both are harmful - check if they have the same harm types
        # Remove 'none' if it somehow appears with other types
        set1.discard("none")
        set2.discard("none")
        
        return set1 == set2
        
    def prompt_with_examples_and_inversion(self, text: str):
        original_result = self.make_new_prompt(text)
        original_harm_types = original_result.get("harm_types", [])
        explanation_original = original_result.get("explanation")
        
        inverted_text = self._invert_prompt(text)
        inverted_result = self.make_new_prompt(inverted_text, commit=False)
        inverted_harm_types = inverted_result.get("harm_types", [])
        explanation_inverted = inverted_result.get("explanation")
        
        # print("OG explanation:", explanation_original, "with harm types:", original_harm_types)
        # print("Inv:", inverted_text)
        # print("Inv explanation:", explanation_inverted, "with harm types:", inverted_harm_types)
        
        match = self._harm_types_match(original_harm_types, inverted_harm_types)
        # print(f"Harm types match: {match}")
        
        return match, inverted_harm_types, inverted_text, explanation_inverted

# Example usage (commented out since it requires API key and examples file)
# context = PrompterContext(examples="examples.json")
# result = context.prompt_with_examples_and_inversion("All people from third world countries are subhuman")
# print(f"Classification is consistent: {result}")
