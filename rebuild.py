import numpy as np
import cv2
import os
from PIL import Image
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F

# Minimal Siamese network for edge similarity
class SiameseEdgeNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((8, 8)),
        )
        self.fc = nn.Sequential(
            nn.Linear(32 * 8 * 8, 128),
            nn.ReLU(),
            nn.Linear(128, 32)
        )
    def forward_once(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x
    def forward(self, x1, x2):
        f1 = self.forward_once(x1)
        f2 = self.forward_once(x2)
        return F.pairwise_distance(f1, f2)

def load_pieces(pieces_dir):
    files = sorted([f for f in os.listdir(pieces_dir) if f.endswith('.png')])
    pieces = [np.array(Image.open(os.path.join(pieces_dir, f))) for f in files]
    return pieces, files

def extract_edges(piece, edge_width=8):
    # Returns a dict of edge arrays: 'top', 'bottom', 'left', 'right'
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

def edge_similarity_siamese(e1, e2, model, device):
    # e1, e2: (H, W, 3) numpy arrays
    # Convert to torch tensor, shape (1, 3, H, W)
    t1 = torch.from_numpy(e1.transpose(2, 0, 1)).float().unsqueeze(0) / 255.0
    t2 = torch.from_numpy(e2.transpose(2, 0, 1)).float().unsqueeze(0) / 255.0
    t1, t2 = t1.to(device), t2.to(device)
    with torch.no_grad():
        dist = model(t1, t2).item()
    return dist

def greedy_reconstruct(pieces, use_siamese=False, model=None, device=None):
    n = len(pieces)
    edges = [extract_edges(p) for p in pieces]
    grid_size = int(np.ceil(np.sqrt(n)))
    placement = np.full((grid_size, grid_size), -1, dtype=int)
    used = set()
    # Place the first piece in the center for better expansion
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
                # Only consider cells adjacent to already placed pieces
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
                    continue  # Only fill cells adjacent to placed pieces
                for p_idx in range(n):
                    if p_idx in used:
                        continue
                    score = 0
                    for side, neighbor_idx, neighbor_side in candidates:
                        if use_siamese and model is not None:
                            score += edge_similarity_siamese(
                                edges[p_idx][side],
                                edges[neighbor_idx][neighbor_side],
                                model, device
                            )
                        else:
                            score += edge_similarity_l2(
                                edges[p_idx][side],
                                edges[neighbor_idx][neighbor_side]
                            )
                    if score < best_score:
                        best_score = score
                        best_pos = (i, j)
                        best_piece = p_idx
        # If no adjacent cell found (shouldn't happen), place next unused piece anywhere
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

def assemble_image(pieces, placement):
    # Assume all pieces are the same size as the original image
    h, w = pieces[0].shape[:2]
    canvas = np.zeros((h, w, 4), dtype=np.uint8)
    for piece in pieces:
        mask = piece[..., 3] > 0
        canvas[mask] = piece[mask]
    return canvas

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python rebuild.py <pieces_dir> [output_image] [--siamese]")
        return
    pieces_dir = sys.argv[1]
    output_image = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "reconstructed.png"
    use_siamese = '--siamese' in sys.argv
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SiameseEdgeNet().to(device) if use_siamese else None
    model.eval() if model is not None else None
    pieces, files = load_pieces(pieces_dir)
    placement = greedy_reconstruct(pieces, use_siamese, model, device)
    result = assemble_image(pieces, placement)
    Image.fromarray(result).save(output_image)
    print(f"Saved reconstructed image to {output_image}")
    if use_siamese:
        print("(Note: Siamese network is randomly initialized and untrained)")

if __name__ == "__main__":
    main() 