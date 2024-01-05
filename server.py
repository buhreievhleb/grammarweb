from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import os
import enchant

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'html', 'htm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify(status="error", message="No file part"), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(status="error", message="No selected file"), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result = check_spelling(filepath)
        
        os.remove(filepath)
        return jsonify(status="success", result=result)
    else:
        return jsonify(status="error", message="File type not allowed"), 400

def check_spelling(filepath):
    d = enchant.Dict("en_US.dic")
    with open(filepath, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    texts = soup.find_all(text=True)
    errors = []
    corrected_text = ""

    for text in texts:
        words = text.split()
        corrected_line = ""
        for word in words:
            if not d.check(word):
                errors.append(word)
                corrected_line += "<mark>" + word + "</mark> "
            else:
                corrected_line += word + " "
        corrected_text += corrected_line + "\n"

    return {"misspelled_words": errors, "corrected_text": corrected_text}


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
