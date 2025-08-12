import numpy as np
import cv2
import os
from PIL import Image
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor

def load_piece_file(path):
    return np.array(Image.open(path))

def load_pieces(pieces_dir):
    files = sorted([f for f in os.listdir(pieces_dir) if f.endswith('.png')])
    paths = [os.path.join(pieces_dir, f) for f in files]
    with ThreadPoolExecutor() as executor:
        pieces = list(executor.map(load_piece_file, paths))
    return pieces, files

def extract_edges(piece, edge_width=8):
    mask = piece[..., 3] > 0
    edges = {}
    edges['top'] = piece[:edge_width, :, :3] * mask[:edge_width, :, None]
    edges['bottom'] = piece[-edge_width:, :, :3] * mask[-edge_width:, :, None]
    edges['left'] = piece[:, :edge_width, :3] * mask[:, :edge_width, None]
    edges['right'] = piece[:, -edge_width:, :3] * mask[:, -edge_width:, None]
    return edges

def edge_similarity_l2(e1, e2):
    mask = (np.sum(e1, axis=-1) > 0) & (np.sum(e2, axis=-1) > 0)
    if np.sum(mask) == 0:
        return np.inf
    return np.linalg.norm(e1[mask] - e2[mask]) / np.sum(mask)

def precompute_edge_similarities(edges):
    n = len(edges)
    sim = {}
    with ThreadPoolExecutor() as executor:
        futures = {}
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                for side1, side2 in [('top', 'bottom'), ('bottom', 'top'), ('left', 'right'), ('right', 'left')]:
                    key = (i, j, side1, side2)
                    futures[key] = executor.submit(edge_similarity_l2, edges[i][side1], edges[j][side2])
        for key, fut in futures.items():
            sim[key] = fut.result()
    return sim

def greedy_reconstruct(pieces):
    n = len(pieces)
    with ThreadPoolExecutor() as executor:
        edges = list(executor.map(extract_edges, pieces))
    sim = precompute_edge_similarities(edges)
    grid_size = int(np.ceil(np.sqrt(n)))
    placement = np.full((grid_size, grid_size), -1, dtype=int)
    used = set()
    center = grid_size // 2
    placement[center, center] = 0
    used.add(0)
    
    for idx in range(1, n):
        best_score = np.inf
        best_pos = None
        best_piece = None
        for i in range(grid_size):
            for j in range(grid_size):
                if placement[i, j] != -1:
                    continue
                candidates = []
                if i > 0 and placement[i-1, j] != -1:
                    candidates.append(('top', placement[i-1, j], 'bottom'))
                if j > 0 and placement[i, j-1] != -1:
                    candidates.append(('left', placement[i, j-1], 'right'))
                if i < grid_size-1 and placement[i+1, j] != -1:
                    candidates.append(('bottom', placement[i+1, j], 'top'))
                if j < grid_size-1 and placement[i, j+1] != -1:
                    candidates.append(('right', placement[i, j+1], 'left'))
                if not candidates:
                    continue
                for p_idx in range(n):
                    if p_idx in used:
                        continue
                    score = 0
                    for side, neighbor_idx, neighbor_side in candidates:
                        key = (p_idx, neighbor_idx, side, neighbor_side)
                        score += sim[key]
                    if score < best_score:
                        best_score = score
                        best_pos = (i, j)
                        best_piece = p_idx
        if best_pos is None:
            for i in range(grid_size):
                for j in range(grid_size):
                    if placement[i, j] == -1:
                        for p_idx in range(n):
                            if p_idx not in used:
                                placement[i, j] = p_idx
                                used.add(p_idx)
                                break
                        break
                else:
                    continue
                break
        else:
            placement[best_pos] = best_piece
            used.add(best_piece)
    return placement

def template_based_reconstruct(pieces):
    n = len(pieces)
    grid_size = int(np.ceil(np.sqrt(n)))
    
    gray_pieces = []
    for piece in pieces:
        mask = piece[..., 3] > 0
        gray = np.dot(piece[..., :3], [0.299, 0.587, 0.114])
        gray_pieces.append((gray, mask))
    
    placement = np.full((grid_size, grid_size), -1, dtype=int)
    used = set()
    
    center = grid_size // 2
    best_center = 0
    max_content = 0
    
    for i, (gray, mask) in enumerate(gray_pieces):
        content = np.sum(mask)
        if content > max_content:
            max_content = content
            best_center = i
    
    placement[center, center] = best_center
    used.add(best_center)
    
    def find_best_neighbor(pos_i, pos_j, direction):
        if placement[pos_i, pos_j] == -1:
            return None, np.inf
        
        current_piece_idx = placement[pos_i, pos_j]
        current_gray, current_mask = gray_pieces[current_piece_idx]
        
        best_piece = None
        best_score = np.inf
        
        for piece_idx in range(n):
            if piece_idx in used:
                continue
            
            candidate_gray, candidate_mask = gray_pieces[piece_idx]
            
            if direction == 'right':
                current_edge = current_gray[:, -1] * current_mask[:, -1]
                candidate_edge = candidate_gray[:, 0] * candidate_mask[:, 0]
            elif direction == 'left':
                current_edge = current_gray[:, 0] * current_mask[:, 0]
                candidate_edge = candidate_gray[:, -1] * candidate_mask[:, -1]
            elif direction == 'down':
                current_edge = current_gray[-1, :] * current_mask[-1, :]
                candidate_edge = candidate_gray[0, :] * candidate_mask[0, :]
            elif direction == 'up':
                current_edge = current_gray[0, :] * current_mask[0, :]
                candidate_edge = candidate_gray[-1, :] * candidate_mask[-1, :]
            else:
                continue
            
            valid_mask = (current_edge > 0) & (candidate_edge > 0)
            if np.sum(valid_mask) > 10:
                score = np.mean(np.abs(current_edge[valid_mask] - candidate_edge[valid_mask]))
                if score < best_score:
                    best_score = score
                    best_piece = piece_idx
        
        return best_piece, best_score
    
    queue = [(center, center)]
    
    while queue and len(used) < n:
        i, j = queue.pop(0)
        
        directions = [('right', i, j+1), ('left', i, j-1), ('down', i+1, j), ('up', i-1, j)]
        
        for direction, ni, nj in directions:
            if (0 <= ni < grid_size and 0 <= nj < grid_size and 
                placement[ni, nj] == -1 and len(used) < n):
                
                best_piece, score = find_best_neighbor(i, j, direction)
                
                if best_piece is not None and score < 50:
                    placement[ni, nj] = best_piece
                    used.add(best_piece)
                    queue.append((ni, nj))
    
    unused_pieces = [p for p in range(n) if p not in used]
    piece_idx = 0
    
    for i in range(grid_size):
        for j in range(grid_size):
            if placement[i, j] == -1 and piece_idx < len(unused_pieces):
                placement[i, j] = unused_pieces[piece_idx]
                piece_idx += 1
    
    return placement

def smart_reconstruct(pieces):
    n = len(pieces)
    if n <= 50:
        return greedy_reconstruct(pieces)
    else:
        return template_based_reconstruct(pieces)

def assemble_image(pieces, placement):
    h, w = pieces[0].shape[:2]
    canvas = np.zeros((h, w, 4), dtype=np.uint8)
    for piece in pieces:
        mask = piece[..., 3] > 0
        canvas[mask] = piece[mask]
    return canvas

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python rebuild.py <pieces_dir> [output_image]")
        return
    pieces_dir = sys.argv[1]
    output_image = sys.argv[2] if len(sys.argv) > 2 else "reconstructed.png"
    pieces, files = load_pieces(pieces_dir)
    placement = smart_reconstruct(pieces)
    result = assemble_image(pieces, placement)
    Image.fromarray(result).save(output_image)

if __name__ == "__main__":
    main() 