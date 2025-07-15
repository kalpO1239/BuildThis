import numpy as np
from PIL import Image
import os
import sys

def verify_coverage(original_image_path, pieces_dir, n_pieces=50, output_path=None):
    img = np.array(Image.open(original_image_path).convert("RGBA"))
    height, width = img.shape[:2]
    coverage = np.zeros((height, width), dtype=np.uint8)
    for i in range(n_pieces):
        piece_path = os.path.join(pieces_dir, f"piece_{i:02d}.png")
        if not os.path.exists(piece_path):
            print(f"Missing piece: {piece_path}")
            continue
        piece = np.array(Image.open(piece_path).convert("RGBA"))
        mask = piece[..., 3] > 0
        coverage[mask] += 1
    # Check for gaps (pixels not covered)
    gaps = (coverage == 0)
    overlaps = (coverage > 1)
    print(f"Total pixels: {height*width}")
    print(f"Uncovered pixels: {np.sum(gaps)}")
    print(f"Overlapped pixels: {np.sum(overlaps)}")
    if output_path:
        # Save a visualization: red for gaps, green for overlaps
        vis = np.zeros((height, width, 3), dtype=np.uint8)
        vis[gaps] = [255, 0, 0]
        vis[overlaps] = [0, 255, 0]
        Image.fromarray(vis).save(output_path)
        print(f"Saved coverage visualization to {output_path}")
    if np.sum(gaps) == 0 and np.sum(overlaps) == 0:
        print("SUCCESS: All pixels are covered exactly once by the pieces.")
    else:
        print("WARNING: There are gaps or overlaps in the coverage.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python verify_coverage.py <original_image> <pieces_dir> [n_pieces] [output_vis.png]")
        return
    original_image = sys.argv[1]
    pieces_dir = sys.argv[2]
    n_pieces = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    output_path = sys.argv[4] if len(sys.argv) > 4 else None
    verify_coverage(original_image, pieces_dir, n_pieces, output_path)

if __name__ == "__main__":
    main() 