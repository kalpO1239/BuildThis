from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import shutil
import subprocess
from werkzeug.utils import secure_filename
import zipfile
import io
import time

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

UPLOAD_FOLDER = 'uploads'
PIECES_FOLDER = 'pieces'
REBUILT_FOLDER = 'rebuilt'
ALLOWED_EXTENSIONS = {'png'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REBUILT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PIECES_FOLDER'] = PIECES_FOLDER
app.config['REBUILT_FOLDER'] = REBUILT_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/shatter', methods=['POST'])
def shatter():
    # Always reset pieces and rebuilt folders at the start
    if os.path.exists(PIECES_FOLDER):
        shutil.rmtree(PIECES_FOLDER)
    os.makedirs(PIECES_FOLDER, exist_ok=True)
    if os.path.exists(REBUILT_FOLDER):
        shutil.rmtree(REBUILT_FOLDER)
    os.makedirs(REBUILT_FOLDER, exist_ok=True)
    start_time = time.time()
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        # Run shatter.py
        subprocess.run(['python3', 'shatter.py', upload_path], check=True)
        # List pieces
        pieces = sorted([f for f in os.listdir(PIECES_FOLDER) if f.endswith('.png')])
        piece_urls = [f'/static/pieces/{p}' for p in pieces]
        runtime = time.time() - start_time
        return jsonify({'pieces': piece_urls, 'runtime': runtime})
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/rebuild', methods=['POST'])
def rebuild():
    start_time = time.time()
    data = request.get_json()
    order = data.get('order')
    if not order or len(order) != 50:
        return jsonify({'error': 'Order must be a list of 50 piece filenames'}), 400
    # Copy pieces in the given order to a temp folder
    temp_folder = os.path.join('temp_pieces')
    os.makedirs(temp_folder, exist_ok=True)
    for idx, piece_name in enumerate(order):
        src = os.path.join(PIECES_FOLDER, os.path.basename(piece_name))
        dst = os.path.join(temp_folder, f'piece_{idx:02d}.png')
        shutil.copy(src, dst)
    # Run rebuild.py
    output_path = os.path.join(REBUILT_FOLDER, 'rebuilt.png')
    subprocess.run(['python3', 'rebuild.py', temp_folder, output_path], check=True)
    # Clean up temp folder
    shutil.rmtree(temp_folder)
    runtime = time.time() - start_time
    return jsonify({'rebuilt': '/static/rebuilt/rebuilt.png', 'runtime': runtime})

@app.route('/download_pieces_zip', methods=['GET'])
def download_pieces_zip():
    # Create a zip of the pieces folder in memory
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in sorted(os.listdir(PIECES_FOLDER)):
            file_path = os.path.join(PIECES_FOLDER, filename)
            zf.write(file_path, arcname=filename)
    mem_zip.seek(0)
    return send_file(mem_zip, mimetype='application/zip', as_attachment=True, download_name='pieces.zip')

@app.route('/static/pieces/<path:filename>')
def serve_piece(filename):
    return send_from_directory(PIECES_FOLDER, filename)

@app.route('/static/rebuilt/<path:filename>')
def serve_rebuilt(filename):
    return send_from_directory(REBUILT_FOLDER, filename)

@app.route('/test')
def test():
    return 'CORS is working!'

if __name__ == '__main__':
    app.run(debug=True, threaded=True) 