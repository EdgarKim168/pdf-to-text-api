from flask import Flask, request, jsonify
import pdfplumber
import io

app = Flask(__name__)

@app.route('/')
def home():
    return 'PDF API is running'

@app.route('/extract', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    with pdfplumber.open(io.BytesIO(file.read())) as pdf:
        text = "\n".join([page.extract_text() or "" for page in pdf.pages])

    return jsonify({'text': text})

if __name__ == '__main__':
    app.run()