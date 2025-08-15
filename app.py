import os
import io
import time
import zipfile
import random
import json
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image

from shatter import shatter_jigsaw_interlocking
from rebuild import rebuild_jigsaw  # Updated rebuild import

# ---------------- Flask setup ----------------
app = Flask(__name__)
# Allow CORS for local development frontends
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Define folders for uploads, pieces, and rebuilt images
UPLOAD_FOLDER = 'uploads'
PIECES_FOLDER = 'pieces'
REBUILT_FOLDER = 'rebuilt'
ALLOWED_EXTENSIONS = {'png'}
SHUFFLE_ORDER_FILE = os.path.join(PIECES_FOLDER, "pieces_order.json")

# Make sure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PIECES_FOLDER, exist_ok=True)
os.makedirs(REBUILT_FOLDER, exist_ok=True)

# Configure Flask app with paths
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PIECES_FOLDER'] = PIECES_FOLDER
app.config['REBUILT_FOLDER'] = REBUILT_FOLDER

# ---------------- Utilities ----------------
def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- Shatter Route ----------------
@app.route('/shatter', methods=['POST'])
def shatter():
    """Shatter an uploaded image into jigsaw pieces."""
    total_start = time.time()

    # Validate file upload
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Clear existing pieces folder before shattering
        for f in os.listdir(PIECES_FOLDER):
            if f.endswith('.png'):
                os.remove(os.path.join(PIECES_FOLDER, f))
        if os.path.exists(SHUFFLE_ORDER_FILE):
            os.remove(SHUFFLE_ORDER_FILE)
        
        # Run the shatter algorithm
        shatter_jigsaw_interlocking(upload_path, output_dir=PIECES_FOLDER)
        
        # List the generated pieces
        pieces = sorted([f for f in os.listdir(PIECES_FOLDER) if f.endswith('.png')])
        piece_urls = [f'/static/pieces/{p}' for p in pieces]
        return jsonify({'pieces': piece_urls, 'runtime': time.time()-total_start})
    
    return jsonify({'error': 'Invalid file type'}), 400

# ---------------- Rebuild Route ----------------
@app.route('/rebuild', methods=['POST'])
def rebuild():
    """Rebuild the jigsaw from pieces using geometric + color matching."""
    total_start = time.time()
    
    # Clear rebuilt folder
    for f in os.listdir(REBUILT_FOLDER):
        if f.endswith('.png'):
            os.remove(os.path.join(REBUILT_FOLDER, f))
    
    try:
        output_path = os.path.join(REBUILT_FOLDER, 'reconstructed.png')
        
        # Call the color-aware rebuild algorithm
        assembled = rebuild_jigsaw(
            pieces_folder=PIECES_FOLDER, 
            edges_file=os.path.join(PIECES_FOLDER, 'pieces_edges.json'),
            output_path=output_path
        )
        
        rebuilt_url = '/static/rebuilt/reconstructed.png'
        runtime = time.time() - total_start
        return jsonify({'rebuilt': rebuilt_url, 'runtime': runtime})
    
    except Exception as e:
        # On error, return a blank canvas as fallback
        empty_canvas = Image.new("RGBA", (800, 600), (0, 0, 0, 0))
        empty_canvas.save(os.path.join(REBUILT_FOLDER, 'reconstructed.png'))
        runtime = time.time() - total_start
        return jsonify({
            'error': str(e),
            'rebuilt': '/static/rebuilt/reconstructed.png',
            'runtime': runtime
        }), 500

# ---------------- Shuffle Pieces ----------------
@app.route('/shuffle_pieces', methods=['POST'])
def shuffle_pieces():
    """Randomly shuffle the pieces and save the order."""
    pieces = [f for f in os.listdir(PIECES_FOLDER) if f.endswith('.png')]
    if not pieces:
        return jsonify({'error': 'No pieces to shuffle'}), 400

    random.shuffle(pieces)

    # Save shuffle order for later reference
    with open(SHUFFLE_ORDER_FILE, 'w') as f:
        json.dump(pieces, f)

    # Return shuffled URLs
    piece_urls = [f'/static/pieces/{fname}' for fname in pieces]
    return jsonify({'status': 'shuffled', 'pieces': piece_urls})

# ---------------- Load Pieces ----------------
@app.route('/load_pieces', methods=['GET'])
def load_pieces():
    """Load pieces respecting saved shuffle order."""
    if os.path.exists(SHUFFLE_ORDER_FILE):
        with open(SHUFFLE_ORDER_FILE, 'r') as f:
            pieces = json.load(f)
    else:
        pieces = sorted([f for f in os.listdir(PIECES_FOLDER) if f.endswith('.png')])
    
    piece_urls = [f'/static/pieces/{p}' for p in pieces]
    return jsonify({'pieces': piece_urls})

# ---------------- Load Pieces from Zip ----------------
@app.route('/load_zip_pieces', methods=['POST'])
def load_zip_pieces():
    """Extract PNGs from uploaded zip file into the pieces folder."""
    total_start = time.time()
    if 'zip_file' not in request.files:
        return jsonify({'error': 'No zip file uploaded'}), 400
    zip_file = request.files['zip_file']
    
    if zip_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not zip_file.filename.endswith('.zip'):
        return jsonify({'error': 'File must be a zip'}), 400
    
    try:
        # Clear existing pieces & shuffle file
        for f in os.listdir(PIECES_FOLDER):
            if f.endswith('.png'):
                os.remove(os.path.join(PIECES_FOLDER, f))
        if os.path.exists(SHUFFLE_ORDER_FILE):
            os.remove(SHUFFLE_ORDER_FILE)
        
        # Extract PNGs from zip
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            png_files = [f for f in zip_ref.namelist() if f.endswith('.png')]
            for png_file in png_files:
                zip_ref.extract(png_file, PIECES_FOLDER)
                # Flatten subfolders
                extracted_path = os.path.join(PIECES_FOLDER, png_file)
                if os.path.dirname(png_file):
                    filename = os.path.basename(png_file)
                    new_path = os.path.join(PIECES_FOLDER, filename)
                    if os.path.exists(extracted_path):
                        os.rename(extracted_path, new_path)
        
        pieces = sorted([f for f in os.listdir(PIECES_FOLDER) if f.endswith('.png')])
        piece_urls = [f'/static/pieces/{p}' for p in pieces]
        return jsonify({'pieces': piece_urls, 'runtime': time.time()-total_start})
    
    except zipfile.BadZipFile:
        return jsonify({'error': 'Invalid zip file'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing zip: {str(e)}'}, 500)

# ---------------- Download Pieces as Zip ----------------
@app.route('/download_pieces_zip', methods=['GET'])
def download_pieces_zip():
    """Download all pieces as a zip archive."""
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in sorted(os.listdir(PIECES_FOLDER)):
            file_path = os.path.join(PIECES_FOLDER, filename)
            zf.write(file_path, arcname=filename)
    mem_zip.seek(0)
    return send_file(mem_zip, mimetype='application/zip', as_attachment=True, download_name='pieces.zip')

# ---------------- Serve Static ----------------
@app.route('/static/pieces/<path:filename>')
def serve_piece(filename):
    """Serve individual piece images."""
    return send_from_directory(PIECES_FOLDER, filename)

@app.route('/static/rebuilt/<path:filename>')
def serve_rebuilt(filename):
    """Serve the reconstructed jigsaw image."""
    return send_from_directory(REBUILT_FOLDER, filename)

# ---------------- Test Route ----------------
@app.route('/test')
def test():
    """Simple test to verify server & CORS."""
    return 'CORS is working!'

# ---------------- Main ----------------
if __name__ == '__main__':
    app.run(debug=False, threaded=True, host='127.0.0.1', port=5001)
