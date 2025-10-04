from flask import Flask, request, jsonify
import os
from AtoT import transcribe_audio  # Make sure this import works in your environment

app = Flask(__name__)
# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp4', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/audio/analyze', methods=['POST'])
def analyze_audio():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    # If user does not select file, browser submits an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Save the file to the upload folder
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Transcribe the audio file using your AtoT module
        tx = transcribe_audio(filepath, sentence_timestamps=True)

        # Prepare the response with full transcript and sentence timings
        sentences = [
            {
                "text": s.text,
                "start": s.start,
                "end": s.end,
                "duration": s.end - s.start
            }
            for i, s in enumerate(tx.sentences, 1)
        ]

        return jsonify({
            "status": "success",
            "full_transcript": tx.text,
            "sentences": sentences,
            "metadata": {
                "filename": file.filename,
                "filepath": filepath
            }
        })

    return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
