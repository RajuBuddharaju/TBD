import requests
import json
import re
import pretrained

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
                for ex in self.examples:
                    ex["Toxicity"] = pretrained.get_hate_confidence(ex["Transcript"])
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
        toxicity = pretrained.get_hate_confidence(transcript)

        # Add the final example to be labeled
        content_lines.append("Using the above examples, complete the final label and explanation:\n")
        content_lines.append(f"Transcript: {transcript}")
        content_lines.append(f"Toxicity: {toxicity}")

        new_history_item = self._make_request("\n".join(content_lines)) | {
            "Transcript": transcript,
            "Toxicity": f"{toxicity}",
        }
        self.history.append(new_history_item)
        return new_history_item

    def content_lines(self) -> list[str]:
        content_lines = ["Using these examples, complete the final label:"]
        for ex in self.examples:
            content_lines.append(f"Transcript: {ex['Transcript']}")
            content_lines.append(f"Toxicity: {ex['Toxicity']}")
            content_lines.append(f"Hatespeech: {ex['Hatespeech']}")
            content_lines.append(f"Explanation: {ex['Explanation']}\n")

        for ex in self.history:
            content_lines.append(f"Transcript: {ex['Transcript']}")
            content_lines.append(f"Toxicity: {ex['Toxicity']}")
            content_lines.append(f"Hatespeech: {ex['Hatespeech']}")
            content_lines.append(f"Explanation: {ex['Explanation']}\n")

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
            "temperature": 0.1
        }

        # Make the request
        return self._handle_response(
            requests.post(self.url, headers=headers, json=request)
        )

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        if response.status_code == 200:
            result_string = response.json()['choices'][0]['message']['content']

            # TODO: use json format here
            # Updated regex to match "Hatespeech: true/false"
            hatespeech_match = re.search(r"Hatespeech:\s*(.*)", result_string)
            explanation_match = re.search(r"Explanation:\s*(.*)", result_string, re.DOTALL)

            # Get the extracted values
            hatespeech = hatespeech_match.group(1).strip().lower() if hatespeech_match else None
            explanation = explanation_match.group(1).strip() if explanation_match else None

            # Convert to boolean if needed (optional)
            if hatespeech in ("true", "false"):
                hatespeech = hatespeech == "true"

            return {
                "Hatespeech": hatespeech,
                "Explanation": explanation
            }
        else:
            raise Exception(f"Got error response from Mistral ({response.status_code}): {response.text}")

if __name__ == "__main__":
    ctx = PrompterContext("examples.json")
    print(ctx.make_new_prompt('We love the men!'))
    print(ctx.make_new_prompt('We love the women!'))
