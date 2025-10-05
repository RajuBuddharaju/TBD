import os

from flask import Flask, request, jsonify, session

from AtoT import transcribe_audio
from prompter import PrompterContext

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {"wav", "mp3", "mp4", "webm"}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "changeme"


def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/audio/analyze', methods=['POST'])
def analyze_audio():
    if "prompter_ctx" not in session.keys() or not session["prompter_ctx"]:
        session["prompter_ctx"] = PrompterContext("examples.json").to_dict()

    prompter_ctx = PrompterContext.from_dict(session["prompter_ctx"])

    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    # If user does not select file, browser submits an empty part without filename
    if not file.filename:
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Save the file to the upload folder
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Transcribe the audio file using your AtoT module
        tx = transcribe_audio(filepath, sentence_timestamps=True, model_size="small")
        
        # Process each sentence and perform inversion testing
        inversion_results = []
        for i, s in enumerate(tx.sentences, 1):
            match, inverted_text, inverted_harm_types, explanation_inverted = prompter_ctx.prompt_with_examples_and_inversion(s.text)
            inversion_results.append({
                "match": match,
                "inverted_text": inverted_text,
                "inverted_harm_types": inverted_harm_types,
                "explanation_inverted": explanation_inverted
            })

        # Prepare the response with full transcript and sentence timings
        sentences = [
            {
                "text": s.text,
                "start": s.start,
                "end": s.end,
                "duration": s.end - s.start,
                "harm_types": result["harm_types"],
                "explanation": result["explanation"],
                "inverted_text": inversion["inverted_text"],
                "inverted_harm_types": inversion["inverted_harm_types"],
                "explanation_inverted": inversion["explanation_inverted"],
                "double_standard_detected": not inversion["match"]
            }
            for s, result, inversion in zip(tx.sentences, prompter_ctx.history, inversion_results)
        ]

        print(sentences[0]["harm_types"])

        return jsonify({
            "status": "success",
            "full_transcript": tx.text,
            "sentences": sentences,
            "metadata": {
                "filename": file.filename,
                "filepath": filepath,
                "total_double_standards": sum(1 for sent in sentences if sent["double_standard_detected"])
            }
        })

    return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
