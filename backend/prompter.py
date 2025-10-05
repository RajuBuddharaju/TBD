import requests
import json

from typing import Any

class PrompterContext:
    examples: list[dict[str, Any]]
    history: list[dict[str, Any]]
    api_key: str
    url: str = "https://api.mistral.ai/v1/chat/completions"

    def __init__(self, examples: str | list[dict[str, Any]], url: str | None = None, history: list[dict[str, Any]] = []):
        self.history = []
        self.api_key = PrompterContext._load_api_key()

        if isinstance(examples, str):
            with open(examples, "r") as f:
                self.examples = json.load(f)
        else:
            self.examples = examples

        if url is not None:
            self.url = url 

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


    def make_new_prompt(self, transcript: str):
        content_lines = self.content_lines()

        # Add the final example to be labeled
        content_lines.append("Using the above examples, complete the final label and explanation:\n")
        content_lines.append(f"\n    \"transcript\": {transcript},\n")

        new_history_item = self._make_request("\n".join(content_lines)) | {
            "transcript": transcript,
        }
        self.history.append(new_history_item)
        return new_history_item

    def content_lines(self) -> list[str]:
        content_lines = ["Using these examples, complete the final label. You must give your response as a JSON object following the schema."]
        content_lines.append(json.dumps(self.examples))
        content_lines.append("From here on out, the sentences you are given are all part of the same monologue or message. Please take previous sentences as context into account when making your judgement.")
        content_lines.append(json.dumps(self.history))

        return content_lines
def handle_response(response):
    if response.status_code == 200:
        result_string = response.json()['choices'][0]['message']['content']
>>>>>>> Stashed changes

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
                            "label": {
                                "type": "string",
                                "enum": ["hatespeech", "potential hatespeech", "not hatespeech"],
                                "description": "Classification label indicating the level or presence of hate speech."
                            },
                            "explanation": {
                                "type": "string",
                                "description": "A brief explanation or reasoning for the assigned label."
                            }
                        },
                        "required": ["transcript", "label", "explanation"],
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

if __name__ == "__main__":
    ctx = PrompterContext("examples.json")
    print(ctx.make_new_prompt('We love the men!'))
    print(ctx.make_new_prompt('We love the women!'))
def prompt_with_examples(text):
    # Load the key
    API_KEY = load_api_key("API.key")

    # Produce request content
    content_str = build_content_from_json("examples.json", text)
    
    # Get response from make_request 
    response = make_request(API_KEY, content_str)
    
    # Handle the response
    return handle_response(response)

def invert_prompt(to_invert):
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
                
    return get_response_from_query(invert_query)
    
def prompt_with_examples_and_inversion(text):
    original_result, explanation_original = prompt_with_examples(text)
    inverted_text = invert_prompt(text)
    inverted_result, explanation_inverted = prompt_with_examples(inverted_text)
    print("OG explanation:",explanation_original, "with result:", original_result)
    
    print("Inv:", inverted_text)
    print("Inv explanation:", explanation_inverted)
    return original_result == inverted_result
    
print(prompt_with_examples_and_inversion("All people from third world countries are subhuman"))
