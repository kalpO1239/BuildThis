# rebuild.py
import os
import json
import numpy as np
from PIL import Image
from skimage import color

# ---------------- Configuration ----------------
ROWS = 5
COLS = 10
TAB_RADIUS = 20        # same tab radius as used in shatter.py
COLOR_SAMPLE = 20      # number of pixels sampled along edge for color matching
TOP_CANDIDATES = 5     # only try the top N candidates by color score first

def rebuild_jigsaw(pieces_folder="pieces",
                   edges_file="pieces/pieces_edges.json",
                   output_path="rebuilt/reconstructed.png",
                   shuffle_file="pieces/pieces_order.json"):

    # ---------------- Load piece edge definitions ----------------
    # Each piece has a list of 4 edge values: [top, right, bottom, left]
    # 2 = flat, 1 = tab, -1 = slot
    with open(edges_file, "r") as f:
        piece_edges = json.load(f)

    # ---------------- Load piece images ----------------
    piece_map = {}
    for fname in os.listdir(pieces_folder):
        if fname.endswith(".png"):
            piece_map[fname] = Image.open(os.path.join(pieces_folder, fname)).convert("RGBA")
    if not piece_map:
        raise ValueError("No pieces found")

    # ---------------- Determine piece dimensions ----------------
    sample_img = next(iter(piece_map.values()))
    pw, ph = sample_img.size
    # remove tab margins to get actual puzzle piece area
    pw -= 2 * TAB_RADIUS
    ph -= 2 * TAB_RADIUS
    # create blank canvas large enough to hold full reconstructed image
    canvas = Image.new("RGBA", (COLS*pw + 2*TAB_RADIUS, ROWS*ph + 2*TAB_RADIUS), (255,255,255,255))

    # ---------------- Load shuffle order if exists ----------------
    if os.path.exists(shuffle_file):
        with open(shuffle_file,"r") as f:
            shuffle_order = json.load(f)
    else:
        shuffle_order = list(piece_map.keys())

    # ---------------- Categorize pieces ----------------
    # Corner pieces have 2 flat edges, edge pieces have 1 flat, interior none
    corner_pieces = []
    edge_pieces = []
    interior_pieces = []
    for name in shuffle_order:
        e = piece_edges[name]
        flat = e.count(2)
        if flat == 2:
            corner_pieces.append(name)
        elif flat == 1:
            edge_pieces.append(name)
        else:
            interior_pieces.append(name)

    # ---------------- Precompute LAB color signatures for edges ----------------
    # This allows fast color comparisons during placement
    def extract_edge_signature(img, direction):
        """Sample pixels along a piece edge and convert to LAB color space."""
        img = img.copy()
        if direction == 'top':
            edge = img.crop((TAB_RADIUS, TAB_RADIUS, TAB_RADIUS+pw, TAB_RADIUS+COLOR_SAMPLE))
        elif direction == 'bottom':
            edge = img.crop((TAB_RADIUS, TAB_RADIUS+ph-COLOR_SAMPLE, TAB_RADIUS+pw, TAB_RADIUS+ph))
        elif direction == 'left':
            edge = img.crop((TAB_RADIUS, TAB_RADIUS, TAB_RADIUS+COLOR_SAMPLE, TAB_RADIUS+ph))
        elif direction == 'right':
            edge = img.crop((TAB_RADIUS+pw-COLOR_SAMPLE, TAB_RADIUS, TAB_RADIUS+pw, TAB_RADIUS+ph))
        arr = np.array(edge)[:,:,:3]          # drop alpha channel
        arr = arr.reshape(-1,3) / 255.0      # normalize to 0..1
        lab = color.rgb2lab(arr[np.newaxis,:,:])  # convert to LAB
        return lab[0]

    # Compute LAB signatures for all pieces & all edges
    edge_sigs = {}
    for name, img in piece_map.items():
        edge_sigs[name] = {
            'top': extract_edge_signature(img, 'top'),
            'bottom': extract_edge_signature(img, 'bottom'),
            'left': extract_edge_signature(img, 'left'),
            'right': extract_edge_signature(img, 'right'),
        }

    # ---------------- Placement data ----------------
    placed = {}  # (row,col) -> piece name
    used = set() # track which pieces are already placed

    # ---------------- Validity check ----------------
    def is_valid(name, r, c):
        """Check if a piece can be placed at (r,c) considering neighbor edges and borders."""
        e = piece_edges[name]
        # top neighbor must match
        if r>0:
            top = placed[(r-1,c)]
            if e[0] != -piece_edges[top][2]:
                return False
        # left neighbor must match
        if c>0:
            left = placed[(r,c-1)]
            if e[3] != -piece_edges[left][1]:
                return False
        # enforce border flat edges
        if r==0 and e[0]!=2: return False
        if r==ROWS-1 and e[2]!=2: return False
        if c==0 and e[3]!=2: return False
        if c==COLS-1 and e[1]!=2: return False
        return True

    # ---------------- Color scoring ----------------
    def color_score(name, r, c):
        """Compute color difference between candidate piece and its neighbors."""
        score = 0.0
        # top neighbor
        if r>0:
            top_name = placed[(r-1,c)]
            score += np.mean((edge_sigs[name]['top'] - edge_sigs[top_name]['bottom'])**2)
        # left neighbor
        if c>0:
            left_name = placed[(r,c-1)]
            score += np.mean((edge_sigs[name]['left'] - edge_sigs[left_name]['right'])**2)
        return score

    # ---------------- Next empty cell ----------------
    def next_cell():
        """Return the next empty (row,col) cell to fill."""
        for r in range(ROWS):
            for c in range(COLS):
                if (r,c) not in placed:
                    return r,c
        return None,None

    # ---------------- Backtracking placement ----------------
    def backtrack():
        r,c = next_cell()
        if r is None:
            return True  # all cells placed
        # select candidate list based on piece type
        is_corner = (r==0 or r==ROWS-1) and (c==0 or c==COLS-1)
        is_edge = (r==0 or r==ROWS-1 or c==0 or c==COLS-1) and not is_corner
        if is_corner:
            candidates = corner_pieces
        elif is_edge:
            candidates = edge_pieces
        else:
            candidates = interior_pieces
        # filter candidates that are valid and not used
        valids = [n for n in candidates if n not in used and is_valid(n,r,c)]
        # sort by color similarity (smaller score = better match)
        ranked = sorted(valids, key=lambda n: color_score(n,r,c))
        # try top candidates first
        for name in ranked[:TOP_CANDIDATES]:
            placed[(r,c)] = name
            used.add(name)
            if backtrack():
                return True
            # undo if failed
            del placed[(r,c)]
            used.remove(name)
        return False

    # ---------------- Solve puzzle ----------------
    solved = backtrack()
    if not solved:
        raise ValueError("No valid solution")

    # ---------------- Paste pieces onto canvas ----------------
    for (r,c), name in placed.items():
        canvas.paste(piece_map[name], (c*pw,r*ph), piece_map[name])

    # Save final reconstructed image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    canvas.save(output_path)
    return np.array(canvas)

# ---------------- Main ----------------
if __name__=="__main__":
    rebuild_jigsaw()
