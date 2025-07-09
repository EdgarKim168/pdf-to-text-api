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
    entries = []
    start_extracting = False

    with pdfplumber.open(io.BytesIO(file.read())) as pdf:
        lines = []
        for page in pdf.pages:
            line_chars = {}
            for char in page.chars:
                top = round(char['top'])  # group visually by line
                if top not in line_chars:
                    line_chars[top] = []
                line_chars[top].append(char)

            for top in sorted(line_chars.keys()):
                chars = sorted(line_chars[top], key=lambda c: c['x0'])
                line_text = ''.join([c['text'] for c in chars])
                fontnames = set(c['fontname'].lower() for c in chars)
                is_bold = any("bold" in f or "black" in f for f in fontnames)

                # Wait until "Item Description" is found
                if not start_extracting:
                    if "item description" in line_text.lower():
                        start_extracting = True
                    continue

                lines.append({
                    'text': line_text.strip(),
                    'is_bold': is_bold
                })

    # Process the lines into product entries
    i = 0
    while i < len(lines):
        if lines[i]['is_bold']:
            nama_produk = lines[i]['text']
            deskripsi_produk = ""

            if i + 1 < len(lines) and not lines[i + 1]['is_bold']:
                deskripsi_produk = lines[i + 1]['text']
                i += 1  # skip next line

            entries.append({
                "Nama_Produk": nama_produk,
                "Deskripsi_Produk": deskripsi_produk
            })
        i += 1

    return jsonify({'data': entries})

if __name__ == '__main__':
    app.run()
