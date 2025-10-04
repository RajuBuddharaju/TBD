import requests
import json
import re

# Load API key from a local file
def load_api_key(filename="API.key"):
    try:
        with open(filename, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise Exception(f"API key file '{filename}' not found.")
    except Exception as e:
        raise Exception(f"Error reading API key: {e}")

def build_content_from_json(json_filepath, final_transcript, final_toxicity):
    """
    Reads labeled examples from a JSON file and builds a prompt content string.
    
    Args:
        json_filepath (str): Path to the JSON file containing labeled examples.
        final_transcript (str): The transcript for which the label is to be predicted.
        final_toxicity (float): The toxicity score of the final transcript.
    
    Returns:
        str: A formatted prompt string ready to be sent to the model.
    """
    with open(json_filepath, "r") as f:
        examples = json.load(f)
    
    # Build the examples part
    content_lines = ["Using these examples, complete the final label:\n"]
    
    for ex in examples:
        content_lines.append(f"Transcript: {ex['Transcript']}")
        content_lines.append(f"Toxicity: {ex['Toxicity']}%")
        content_lines.append(f"Label: {ex['Label']}")
        content_lines.append(f"Explanation: {ex['Explanation']}\n")
    
    # Add the final example to be labeled
    content_lines.append("Using the above examples, complete the final label and explanation:\n")
    content_lines.append(f"Transcript: {final_transcript}")
    content_lines.append(f"Toxicity: {final_toxicity}%")
    
    return "\n".join(content_lines)

def make_request(API_KEY, content_str):
    # Mistral API endpoint
    url = "https://api.mistral.ai/v1/chat/completions"

    # Set up headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Define the message for the chat
    request_data = {
        "model": "mistral-tiny",  # or "mistral-small", "mistral-medium"
        "messages": [
            {"role": "user", "content": content_str}
        ],
        "temperature": 0.1
    }

    # Make the request
    return requests.post(url, headers=headers, json=request_data)

def handle_response(response):
    if response.status_code == 200:
        result_string = response.json()['choices'][0]['message']['content']
        
        label_match = re.search(r"Label:\s*(.*)", result_string)
        explanation_match = re.search(r"Explanation:\s*(.*)", result_string, re.DOTALL)

        # Get the extracted values
        label = label_match.group(1).strip() if label_match else None
        explanation = explanation_match.group(1).strip() if explanation_match else None
        
        return (label, explanation)
    else:
        print("Error:", response.status_code, response.text)

def prompt_with_examples(text):
    # Load the key
    API_KEY = load_api_key("API.key")

    # Produce request content
    content_str = build_content_from_json("examples.json", text, 50)
    
    # Get response from make_request 
    response = make_request(API_KEY, content_str)
    
    # Handle the response
    return handle_response(response)
