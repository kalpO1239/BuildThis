from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import shutil
import subprocess
from werkzeug.utils import secure_filename
import zipfile
import io
import time
from shatter import voronoi_full_coverage
from rebuild import load_pieces, smart_reconstruct, assemble_image, get_placement_data
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

UPLOAD_FOLDER = 'uploads'
PIECES_FOLDER = 'pieces'
REBUILT_FOLDER = 'rebuilt'
ALLOWED_EXTENSIONS = {'png'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PIECES_FOLDER, exist_ok=True)
os.makedirs(REBUILT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PIECES_FOLDER'] = PIECES_FOLDER
app.config['REBUILT_FOLDER'] = REBUILT_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/shatter', methods=['POST'])
def shatter():
    total_start = time.time()
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        # Get piece count from form data, default to 50
        piece_count = int(request.form.get('piece_count', 50))
        
        # File upload timing
        upload_start = time.time()
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        upload_time = time.time() - upload_start
        
        # Folder cleanup timing
        cleanup_start = time.time()
        # Clear pieces folder efficiently (only if it exists and has files)
        if os.path.exists(PIECES_FOLDER):
            for f in os.listdir(PIECES_FOLDER):
                if f.endswith('.png'):
                    os.remove(os.path.join(PIECES_FOLDER, f))
        else:
            os.makedirs(PIECES_FOLDER, exist_ok=True)
        
        # Clear rebuilt folder efficiently
        if os.path.exists(REBUILT_FOLDER):
            for f in os.listdir(REBUILT_FOLDER):
                if f.endswith('.png'):
                    os.remove(os.path.join(REBUILT_FOLDER, f))
        else:
            os.makedirs(REBUILT_FOLDER, exist_ok=True)
        cleanup_time = time.time() - cleanup_start
        
        # Shatter timing
        shatter_start = time.time()
        voronoi_full_coverage(upload_path, n_pieces=piece_count, output_dir=app.config['PIECES_FOLDER'])
        shatter_time = time.time() - shatter_start
        
        # Response preparation timing
        response_start = time.time()
        pieces = sorted([f for f in os.listdir(PIECES_FOLDER) if f.endswith('.png')])
        piece_urls = [f'/static/pieces/{p}' for p in pieces]
        response_time = time.time() - response_start
        
        total_time = time.time() - total_start
        return jsonify({
            'pieces': piece_urls, 
            'runtime': total_time,
            'timing_breakdown': {
                'upload': upload_time,
                'cleanup': cleanup_time,
                'shatter': shatter_time,
                'response': response_time
            }
        })
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/rebuild', methods=['POST'])
def rebuild():
    total_start = time.time()
    data = request.get_json()
    order = data.get('order')
    if not order:
        return jsonify({'error': 'Order must be a list of piece filenames'}), 400
    
    piece_count = len(order)
    
    # Copy timing
    copy_start = time.time()
    # Clear rebuilt folder efficiently
    if os.path.exists(REBUILT_FOLDER):
        for f in os.listdir(REBUILT_FOLDER):
            if f.endswith('.png'):
                os.remove(os.path.join(REBUILT_FOLDER, f))
    else:
        os.makedirs(REBUILT_FOLDER, exist_ok=True)
    copy_time = time.time() - copy_start
    
    # Load timing
    load_start = time.time()
    pieces, files = load_pieces(app.config['PIECES_FOLDER'])
    load_time = time.time() - load_start
    
    # Reconstruct timing
    reconstruct_start = time.time()
    placement = smart_reconstruct(pieces)
    reconstruct_time = time.time() - reconstruct_start
    
    # Assemble timing
    assemble_start = time.time()
    assembled_image = assemble_image(pieces, placement)
    assemble_time = time.time() - assemble_start
    
    # Get placement data for animation
    placement_data = get_placement_data(pieces, placement)
    
    # Cleanup timing
    cleanup_start = time.time()
    output_path = os.path.join(app.config['REBUILT_FOLDER'], 'reconstructed.png')
    # Convert numpy array to PIL Image before saving
    if isinstance(assembled_image, np.ndarray):
        assembled_image = Image.fromarray(assembled_image)
    assembled_image.save(output_path)
    cleanup_time = time.time() - cleanup_start
    
    total_time = time.time() - total_start
    return jsonify({
        'rebuilt': '/static/rebuilt/reconstructed.png',
        'placement_data': placement_data,
        'runtime': total_time,
        'timing_breakdown': {
            'copy': copy_time,
            'load': load_time,
            'reconstruct': reconstruct_time,
            'assemble': assemble_time,
            'cleanup': cleanup_time
        }
    })

@app.route('/load_zip_pieces', methods=['POST'])
def load_zip_pieces():
    total_start = time.time()
    if 'zip_file' not in request.files:
        return jsonify({'error': 'No zip file uploaded'}), 400
    
    zip_file = request.files['zip_file']
    piece_count = int(request.form.get('piece_count', 50))
    
    if zip_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not zip_file.filename.endswith('.zip'):
        return jsonify({'error': 'File must be a zip file'}), 400
    
    try:
        # Clear pieces folder efficiently
        if os.path.exists(PIECES_FOLDER):
            for f in os.listdir(PIECES_FOLDER):
                if f.endswith('.png'):
                    os.remove(os.path.join(PIECES_FOLDER, f))
        else:
            os.makedirs(PIECES_FOLDER, exist_ok=True)
        
        # Extract zip file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # Get list of PNG files in the zip
            png_files = [f for f in zip_ref.namelist() if f.endswith('.png')]
            
            if len(png_files) != piece_count:
                return jsonify({'error': f'Expected {piece_count} PNG files, found {len(png_files)}'}), 400
            
            # Extract files to pieces folder
            for png_file in png_files:
                zip_ref.extract(png_file, PIECES_FOLDER)
                # Move from subfolder if necessary
                extracted_path = os.path.join(PIECES_FOLDER, png_file)
                if os.path.dirname(png_file):  # If file was in a subfolder
                    filename = os.path.basename(png_file)
                    new_path = os.path.join(PIECES_FOLDER, filename)
                    if os.path.exists(extracted_path):
                        os.rename(extracted_path, new_path)
        
        # Get piece URLs
        pieces = sorted([f for f in os.listdir(PIECES_FOLDER) if f.endswith('.png')])
        piece_urls = [f'/static/pieces/{p}' for p in pieces]
        
        total_time = time.time() - total_start
        return jsonify({
            'pieces': piece_urls,
            'runtime': total_time,
            'timing_breakdown': {
                'extract': total_time
            }
        })
        
    except zipfile.BadZipFile:
        return jsonify({'error': 'Invalid zip file'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing zip file: {str(e)}'}), 500

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
    app.run(debug=False, threaded=True, host='127.0.0.1', port=5001) 