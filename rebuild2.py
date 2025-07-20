import numpy as np
from PIL import Image
import os
import sys

def load_pieces_and_masks(pieces_dir):
    files = sorted([f for f in os.listdir(pieces_dir) if f.endswith('.png')])
    pieces = []
    masks = []
    for f in files:
        img = Image.open(os.path.join(pieces_dir, f)).convert('RGBA')
        arr = np.array(img)
        pieces.append(arr)
        masks.append(arr[..., 3] > 0)
    return pieces, masks, files

def extract_edge_type(mask, axis, side, tab_threshold=0.15):
    # axis: 0 for vertical (left/right), 1 for horizontal (top/bottom)
    # side: 0 for left/top, -1 for right/bottom
    edge = mask.take(indices=0 if side == 0 else -1, axis=axis)
    # Find the center of the edge
    center = len(edge) // 2
    # Look for a bump (tab) or indent (hole) in the center region
    window = edge[center - len(edge)//4:center + len(edge)//4]
    mean_val = np.mean(window)
    # If the mean is much higher than the edge average, it's a tab; if much lower, a hole
    if mean_val > 1 - tab_threshold:
        return 1  # tab
    elif mean_val < tab_threshold:
        return -1  # hole
    else:
        return 0  # flat

def analyze_piece_edges(mask):
    # Returns [top, right, bottom, left] edge types
    top = extract_edge_type(mask, axis=0, side=0)
    right = extract_edge_type(mask, axis=1, side=-1)
    bottom = extract_edge_type(mask, axis=0, side=-1)
    left = extract_edge_type(mask, axis=1, side=0)
    return [top, right, bottom, left]

def extract_edge_pixels(piece, mask):
    # Returns dict with RGBA pixel arrays for each edge, masked by alpha
    edges = {}
    # Top
    top_mask = mask[0, :]
    edges['top'] = piece[0, :, :] * top_mask[:, None]
    # Right
    right_mask = mask[:, -1]
    edges['right'] = piece[:, -1, :] * right_mask[:, None]
    # Bottom
    bottom_mask = mask[-1, :]
    edges['bottom'] = piece[-1, :, :] * bottom_mask[:, None]
    # Left
    left_mask = mask[:, 0]
    edges['left'] = piece[:, 0, :] * left_mask[:, None]
    return edges

def edge_l2_distance(e1, e2):
    # Only compare where both are non-transparent
    mask = (e1[..., 3] > 0) & (e2[..., 3] > 0)
    if np.sum(mask) == 0:
        return np.inf
    return np.linalg.norm(e1[mask, :3] - e2[mask, :3]) / np.sum(mask)

def compatible_edges(type1, type2):
    # Only tab/hole pairs are compatible
    return (type1 == 1 and type2 == -1) or (type1 == -1 and type2 == 1)

def assemble_jigsaw(pieces, masks, edge_types, edge_pixels, n_rows, n_cols):
    n = len(pieces)
    piece_h, piece_w = pieces[0].shape[:2]
    grid = np.full((n_rows, n_cols), -1, dtype=int)
    used = set()
    # Start with a corner (0,0)
    grid[0, 0] = 0
    used.add(0)
    for r in range(n_rows):
        for c in range(n_cols):
            if grid[r, c] != -1:
                continue
            candidates = []
            for idx in range(n):
                if idx in used:
                    continue
                score = 0
                valid = True
                # Check top neighbor
                if r > 0 and grid[r-1, c] != -1:
                    n_idx = grid[r-1, c]
                    if not compatible_edges(edge_types[idx][0], edge_types[n_idx][2]):
                        valid = False
                    else:
                        score += edge_l2_distance(edge_pixels[idx]['top'], edge_pixels[n_idx]['bottom'])
                # Check left neighbor
                if c > 0 and grid[r, c-1] != -1:
                    n_idx = grid[r, c-1]
                    if not compatible_edges(edge_types[idx][3], edge_types[n_idx][1]):
                        valid = False
                    else:
                        score += edge_l2_distance(edge_pixels[idx]['left'], edge_pixels[n_idx]['right'])
                if valid:
                    candidates.append((score, idx))
            if candidates:
                best_idx = min(candidates)[1]
                grid[r, c] = best_idx
                used.add(best_idx)
            else:
                # Fallback: place any unused piece
                for idx in range(n):
                    if idx not in used:
                        grid[r, c] = idx
                        used.add(idx)
                        break
    # Compose the final image
    out_h = n_rows * piece_h
    out_w = n_cols * piece_w
    out_img = Image.new('RGBA', (out_w, out_h), (0,0,0,0))
    for r in range(n_rows):
        for c in range(n_cols):
            idx = grid[r, c]
            if idx == -1:
                continue
            # Paste the piece at the correct location using its alpha as mask
            piece_img = Image.fromarray(pieces[idx])
            out_img.paste(piece_img, (c*piece_w, r*piece_h), piece_img)
    return out_img

def main():
    if len(sys.argv) < 2:
        print("Usage: python rebuild2.py <pieces_dir> [output_image] [n_rows] [n_cols]")
        return
    pieces_dir = sys.argv[1]
    output_image = sys.argv[2] if len(sys.argv) > 2 else "reconstructed_jigsaw.png"
    n_rows = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    n_cols = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    pieces, masks, files = load_pieces_and_masks(pieces_dir)
    print(f"Loaded {len(pieces)} pieces.")
    edge_types = [analyze_piece_edges(mask) for mask in masks]
    edge_pixels = [extract_edge_pixels(piece, mask) for piece, mask in zip(pieces, masks)]
    out_img = assemble_jigsaw(pieces, masks, edge_types, edge_pixels, n_rows, n_cols)
    out_img.save(output_image)
    print(f"Saved reconstructed image to {output_image}")

if __name__ == "__main__":
    main() 