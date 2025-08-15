import os
import random
import json
from PIL import Image, ImageDraw, ImageChops
import math

# ---------------- Configuration ----------------
TAB_RADIUS = 20           # radius of puzzle tabs
ROWS = 5                  # number of rows in the puzzle
COLS = 10                 # number of columns in the puzzle
POINTS_PER_TAB = 100      # number of points used to draw smooth tab curves

# ---------------- Grid functions ----------------
def initialize_grid():
    """
    Initialize the grid of pieces.
    Each cell has a list of 4 edges: [top, right, bottom, left].
    Flat borders (2) are applied to the outer edges of the puzzle.
    """
    grid = [[[0, 0, 0, 0] for _ in range(COLS)] for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            north = 2 if r == 0 else 0
            south = 2 if r == ROWS-1 else 0
            west = 2 if c == 0 else 0
            east = 2 if c == COLS-1 else 0
            grid[r][c] = [north, east, south, west]
    return grid

def populate_grid(r, c, grid):
    """
    Recursively assign tabs (-1 = slot, 1 = tab) to each piece's edges.
    Ensures adjacent pieces have complementary edges.
    """
    directions = [(-1,0,0),(0,1,1),(1,0,2),(0,-1,3)]  # (dr,dc,index)
    for dr, dc, idx in directions:
        nr, nc = r+dr, c+dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            if grid[r][c][idx] == 0:
                val = random.choice([-1,1])  # assign tab or slot
                grid[r][c][idx] = val
                opp = (idx+2)%4               # opposite edge index
                grid[nr][nc][opp] = -val      # complementary edge for neighbor
                populate_grid(nr,nc,grid)

# ---------------- Mask creation ----------------
def create_interlocking_mask(pw, ph, top, bottom, left, right):
    """
    Generate a mask for a puzzle piece including tabs.
    The mask defines transparent vs opaque areas for cutting the piece.
    """
    mask = Image.new("L", (pw + 2*TAB_RADIUS, ph + 2*TAB_RADIUS), 0)
    
    # base rectangle for the main piece body
    rect = Image.new("L", mask.size, 0)
    draw_rect = ImageDraw.Draw(rect)
    draw_rect.rectangle([TAB_RADIUS, TAB_RADIUS, TAB_RADIUS+pw, TAB_RADIUS+ph], fill=255)
    mask = ImageChops.add(mask, rect)

    def draw_tab(center, radius, direction, invert=False):
        """
        Draw a semicircular tab (protrusion or slot) along a piece edge.
        """
        tab_mask = Image.new("L", mask.size, 0)
        draw_tab = ImageDraw.Draw(tab_mask)
        points = []
        for i in range(POINTS_PER_TAB + 1):
            t = i / POINTS_PER_TAB
            angle = math.pi * t
            if direction == 'top':
                dx = -radius * math.cos(angle)
                dy = -radius * math.sin(angle) if not invert else radius * math.sin(angle)
            elif direction == 'bottom':
                dx = radius * math.cos(angle)
                dy = radius * math.sin(angle) if not invert else -radius * math.sin(angle)
            elif direction == 'left':
                dx = -radius * math.sin(angle) if not invert else radius * math.sin(angle)
                dy = -radius * math.cos(angle)
            elif direction == 'right':
                dx = radius * math.sin(angle) if not invert else -radius * math.sin(angle)
                dy = radius * math.cos(angle)
            points.append((center[0] + dx, center[1] + dy))

        # ensure tab starts and ends at rectangle border
        if direction == 'top': points[0] = (center[0]-radius, center[1]); points[-1] = (center[0]+radius, center[1])
        if direction == 'bottom': points[0] = (center[0]+radius, center[1]); points[-1] = (center[0]-radius, center[1])
        if direction == 'left': points[0] = (center[0], center[1]+radius); points[-1] = (center[0], center[1]-radius)
        if direction == 'right': points[0] = (center[0], center[1]-radius); points[-1] = (center[0], center[1]+radius)

        draw_tab.polygon(points, fill=255)
        return tab_mask

    # center positions for each edge
    mid_top = (TAB_RADIUS + pw/2, TAB_RADIUS)
    mid_bottom = (TAB_RADIUS + pw/2, TAB_RADIUS + ph)
    mid_left = (TAB_RADIUS, TAB_RADIUS + ph/2)
    mid_right = (TAB_RADIUS + pw, TAB_RADIUS + ph/2)

    # apply tabs or slots to mask
    if top == 1:
        mask = ImageChops.add(mask, draw_tab(mid_top, TAB_RADIUS, 'top', invert=False))
    elif top == -1:
        mask = ImageChops.subtract(mask, draw_tab(mid_top, TAB_RADIUS, 'top', invert=True))

    if bottom == 1:
        mask = ImageChops.add(mask, draw_tab(mid_bottom, TAB_RADIUS, 'bottom', invert=False))
    elif bottom == -1:
        mask = ImageChops.subtract(mask, draw_tab(mid_bottom, TAB_RADIUS, 'bottom', invert=True))

    if left == 1:
        mask = ImageChops.add(mask, draw_tab(mid_left, TAB_RADIUS, 'left', invert=False))
    elif left == -1:
        mask = ImageChops.subtract(mask, draw_tab(mid_left, TAB_RADIUS, 'left', invert=True))

    if right == 1:
        mask = ImageChops.add(mask, draw_tab(mid_right, TAB_RADIUS, 'right', invert=False))
    elif right == -1:
        mask = ImageChops.subtract(mask, draw_tab(mid_right, TAB_RADIUS, 'right', invert=True))

    return mask

# ---------------- Puzzle generation ----------------
def shatter_jigsaw_interlocking(image_path, output_dir="pieces"):
    """
    Shatter an input image into fully interlocking jigsaw pieces.
    Each piece is saved with its RGBA image and edge definitions.
    """
    img = Image.open(image_path).convert("RGBA")
    img_w, img_h = img.size
    os.makedirs(output_dir, exist_ok=True)

    piece_w = img_w // COLS
    piece_h = img_h // ROWS

    # initialize piece grid and populate edges with tabs/slots
    grid = initialize_grid()
    populate_grid(0, 0, grid)

    # save final grid layout
    with open(os.path.join(output_dir, "final_grid.json"), "w") as f:
        json.dump(grid, f, indent=2)

    piece_edges = {}  # piece_name -> [top, right, bottom, left]

    idx = 0
    for r in range(ROWS):
        for c in range(COLS):
            x0 = c * piece_w
            y0 = r * piece_h
            x1 = (c + 1) * piece_w if c < COLS - 1 else img_w
            y1 = (r + 1) * piece_h if r < ROWS - 1 else img_h
            pw, ph = x1 - x0, y1 - y0

            top, right, bottom, left = grid[r][c]

            # generate mask including tabs
            full_mask = create_interlocking_mask(pw, ph, top, bottom, left, right)

            # create piece canvas
            piece = Image.new("RGBA", (pw + 2 * TAB_RADIUS, ph + 2 * TAB_RADIUS), (0, 0, 0, 0))

            # crop main piece body from original image
            piece_part = img.crop((x0, y0, x1, y1))
            body_mask = Image.new("L", piece_part.size, 255)
            piece.paste(piece_part, (TAB_RADIUS, TAB_RADIUS), body_mask)

            # paste neighboring protruding tabs (optional, only if tab exists)
            def paste_tab(dir, neighbor_crop, paste_pos):
                if neighbor_crop.size[0] == 0 or neighbor_crop.size[1] == 0:
                    return
                tab_img = Image.new("RGBA", neighbor_crop.size, (0, 0, 0, 0))
                tab_img.paste(neighbor_crop, (0, 0))
                piece.paste(tab_img, paste_pos, tab_img)

            if top == 1 and r > 0:
                crop = img.crop((x0, max(y0 - TAB_RADIUS, 0), x1, y0))
                paste_tab('top', crop, (TAB_RADIUS, 0))
            if bottom == 1 and r < ROWS - 1:
                crop = img.crop((x0, y1, x1, min(y1 + TAB_RADIUS, img_h)))
                paste_tab('bottom', crop, (TAB_RADIUS, ph + TAB_RADIUS))
            if left == 1 and c > 0:
                crop = img.crop((max(x0 - TAB_RADIUS, 0), y0, x0, y1))
                paste_tab('left', crop, (0, TAB_RADIUS))
            if right == 1 and c < COLS - 1:
                crop = img.crop((x1, y0, min(x1 + TAB_RADIUS, img_w), y1))
                paste_tab('right', crop, (pw + TAB_RADIUS, TAB_RADIUS))

            # apply alpha mask to piece to handle transparency around tabs
            piece.putalpha(full_mask)

            # save piece
            piece_name = f"piece_{idx:03d}.png"
            piece.save(os.path.join(output_dir, piece_name))
            piece_edges[piece_name] = [top, right, bottom, left]
            idx += 1

    # save edges mapping
    with open(os.path.join(output_dir, "pieces_edges.json"), "w") as f:
        json.dump(piece_edges, f, indent=2)

    print(f"Saved {idx} fully interlocking pieces to {output_dir}")


# ---------------- Command line support ----------------
if __name__ == "__main__":
    import sys
    if len(sys.argv)<2:
        print("Usage: python shatter.py <image_path> [output_dir]")
        sys.exit(1)
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv)>2 else "pieces"
    shatter_jigsaw_interlocking(image_path, output_dir)
