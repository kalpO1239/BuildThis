# Jigsaw Puzzle Shatter & Rebuild Application

This project allows you to **shatter an image into interlocking jigsaw pieces** and **reconstruct the original image** using a color-aware algorithm. It provides a Flask API for uploading, shattering, shuffling, and rebuilding puzzle images.

---

## Features

- **Shatter Images:** Breaks an input image into fully interlocking jigsaw pieces, including tabs and slots.  
- **Rebuild Puzzle:** Attempts to reconstruct the original image using edge shapes and color matching.  
- **Shuffle Pieces:** Randomly shuffle pieces and preserve shuffle order.  
- **Load Pieces from Zip:** Load puzzle pieces from a zip file.  
- **Download Pieces:** Download all puzzle pieces as a zip file.  
- **Web API:** Flask server with endpoints for shattering, rebuilding, and managing pieces.  
- **CORS Support:** Works with frontend clients on `localhost:3000`.

---

## Installation

1. Clone this repository:
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2. Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

### **Run the Flask server**
```bash
python app.py
