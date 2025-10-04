"""
Hate Speech Detection Pipeline
------------------------------
- Transcribes speech to text using Whisper (AtoT.py)
- Classifies each sentence using unitary/toxic-bert
- Outputs timestamped classifications to classified_output.json
- Provides optional direct text-based hate confidence testing
"""

# === Imports ===
from AtoT import transcribe_audio
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import json


# === 1. Model Setup ===

MODEL_NAME = "unitary/toxic-bert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

HATE_THRESHOLD = 0.5  # adjustable threshold for multi-label detection


# === 2. Core Classification Functions ===
def classify_text(text: str):
    """
    Run toxic-bert classification on a single sentence.

    Returns:
        dict[label -> probability]
    """
    inputs = tokenizer(text, truncation=True, padding=True, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=-1).squeeze()
    labels = model.config.id2label
    return {labels[i]: float(probs[i]) for i in range(len(labels))}


def get_labels(scores):
    """
    Return all labels above the confidence threshold.
    """
    active_labels = [label for label, score in scores.items() if score >= HATE_THRESHOLD]
    return active_labels or ["neutral"]


def get_hate_confidence(text: str) -> float:
    """
    Compute an overall 'hate speech confidence' score for the text.
    Uses relevant toxic-bert output categories.
    """
    scores = classify_text(text)
    hate_labels = ["toxic", "severe_toxic", "threat", "insult", "identity_hate"]
    hate_scores = [scores[lbl] for lbl in hate_labels if lbl in scores]

    if not hate_scores:
        return 0.0

    # Option 1: strongest signal (max)
    hate_confidence = max(hate_scores)

    # Option 2 (alternative): average for smoother scoring
    # hate_confidence = sum(hate_scores) / len(hate_scores)

    return round(hate_confidence, 4)


# === 3. Explanation Logic ===
def explain_classification(text, scores):
    """
    Generate a human-readable explanation for the classification.
    Adds context based on common hate/violence patterns.
    """
    label = max(scores, key=scores.get)
    conf = scores[label]

    explanations = {
        "toxic": "contains hostile or strongly negative language directed at someone or something.",
        "severe_toxic": "contains extremely hostile or aggressive speech that could incite violence or severe harm.",
        "obscene": "contains explicit, profane, or highly offensive words.",
        "threat": "includes language implying or encouraging harm, danger, or violence.",
        "insult": "includes name-calling, belittling, or mocking language toward a person or group.",
        "identity_hate": "targets a specific group or identity (e.g., nationality, race, gender, or religion) in a hateful way."
    }

    # Handle uncertainty
    if conf < 0.4:
        return f"The model was uncertain, but the sentence may {explanations.get(label, 'contain problematic language')}"

    lowered = text.lower()
    context_note = ""
    if "kill" in lowered or "die" in lowered:
        context_note = " It references violence or death."
    elif "hate" in lowered:
        context_note = " It expresses explicit hatred."
    elif any(word in lowered for word in ["idiot", "stupid", "dumb"]):
        context_note = " It includes insulting language."

    return f"This sentence {explanations.get(label, 'may contain harmful content')}{context_note}"


# === 4. Audio → Text → Classification Pipeline ===
def classify_audio_file(audio_path: str, output_path: str = "classified_output.json"):
    """
    Transcribe audio, classify each sentence, and save results to JSON.
    """
    print(f"🎙️ Transcribing audio: {audio_path}")
    tx = transcribe_audio(audio_path, sentence_timestamps=True, vad_filter=False)

    results = []
    for s in tx.sentences:
        scores = classify_text(s.text)
        labels = get_labels(scores)
        confidence = max(scores[lbl] for lbl in labels if lbl in scores) if labels != ["neutral"] else 0.0
        explanation = explain_classification(s.text, scores)

        results.append({
            "start": s.start,
            "end": s.end,
            "text": s.text,
            "labels": labels,
            "confidence": confidence,
            "scores": scores,
            "explanation": explanation
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Classification complete. Results saved to {output_path}")


# === 5. Direct Text Testing (no audio) ===
def test_sample_texts(sample_texts, output_path: str = "hate_confidence_results.json"):
    """
    Test the hate confidence function on predefined sample texts.
    Saves output as JSON.
    """
    results = []
    for text in sample_texts:
        conf = get_hate_confidence(text)
        results.append({
            "text": text,
            "hate_confidence": conf
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Results saved to {output_path}")


# # === 6. Main Entry Point ===

# if __name__ == "__main__":
#     # --- Option A: full pipeline (audio → classification) ---
#     # classify_audio_file("C:\\Users\\baydi\\Downloads\\hatespeech-junctionx.mp4")

#     # --- Option B: quick text-based confidence testing ---
#     test_sample_texts()