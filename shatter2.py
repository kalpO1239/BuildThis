import numpy as np
from PIL import Image, ImageDraw
import os
import sys

def random_tab():
    return np.random.choice([-1, 1])

def create_grid_masks(rows, cols, piece_w, piece_h, tab_radius=18, seed=42):
    np.random.seed(seed)
    masks = [[None for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            mask = Image.new('L', (piece_w + 2*tab_radius, piece_h + 2*tab_radius), 0)
            draw = ImageDraw.Draw(mask)
            # Draw the base rectangle in the center
            draw.rectangle([tab_radius, tab_radius, tab_radius + piece_w - 1, tab_radius + piece_h - 1], fill=255)
            masks[r][c] = mask
    edge_types = {}
    for r in range(rows):
        for c in range(cols):
            if c < cols - 1:
                tab = random_tab()
                edge_types[(r, c, 'right')] = tab
                edge_types[(r, c+1, 'left')] = -tab
            if r < rows - 1:
                tab = random_tab()
                edge_types[(r, c, 'bottom')] = tab
                edge_types[(r+1, c, 'top')] = -tab
    for r in range(rows):
        for c in range(cols):
            mask = masks[r][c]
            draw = ImageDraw.Draw(mask)
            # Top edge
            if (r, c, 'top') in edge_types:
                tab = edge_types[(r, c, 'top')]
                cx = tab_radius + piece_w // 2
                cy = tab_radius
                bbox = [cx - tab_radius, cy - tab_radius, cx + tab_radius, cy + tab_radius]
                if tab == 1:
                    draw.pieslice(bbox, 180, 360, fill=255)  # Tab: add extension
                elif tab == -1:
                    draw.pieslice(bbox, 180, 360, fill=0)    # Hole: subtract bite
            # Right edge
            if (r, c, 'right') in edge_types:
                tab = edge_types[(r, c, 'right')]
                cx = tab_radius + piece_w
                cy = tab_radius + piece_h // 2
                bbox = [cx - tab_radius, cy - tab_radius, cx + tab_radius, cy + tab_radius]
                if tab == 1:
                    draw.pieslice(bbox, 270, 450, fill=255)
                elif tab == -1:
                    draw.pieslice(bbox, 270, 450, fill=0)
            # Bottom edge
            if (r, c, 'bottom') in edge_types:
                tab = edge_types[(r, c, 'bottom')]
                cx = tab_radius + piece_w // 2
                cy = tab_radius + piece_h
                bbox = [cx - tab_radius, cy - tab_radius, cx + tab_radius, cy + tab_radius]
                if tab == 1:
                    draw.pieslice(bbox, 0, 180, fill=255)
                elif tab == -1:
                    draw.pieslice(bbox, 0, 180, fill=0)
            # Left edge
            if (r, c, 'left') in edge_types:
                tab = edge_types[(r, c, 'left')]
                cx = tab_radius
                cy = tab_radius + piece_h // 2
                bbox = [cx - tab_radius, cy - tab_radius, cx + tab_radius, cy + tab_radius]
                if tab == 1:
                    draw.pieslice(bbox, 90, 270, fill=255)
                elif tab == -1:
                    draw.pieslice(bbox, 90, 270, fill=0)
            masks[r][c] = mask
    return masks, edge_types, tab_radius

def shatter2(image_path, n_rows=5, n_cols=10, output_dir="pieces_jigsaw", seed=42):
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    piece_w = width // n_cols
    piece_h = height // n_rows
    tab_radius = int(min(piece_w, piece_h) * 0.3)
    masks, edge_types, tab_radius = create_grid_masks(n_rows, n_cols, piece_w, piece_h, tab_radius=tab_radius, seed=seed)
    all_masks = np.zeros((height, width), dtype=np.uint8)
    for r in range(n_rows):
        for c in range(n_cols):
            left = c * piece_w - tab_radius
            upper = r * piece_h - tab_radius
            right = (c + 1) * piece_w + tab_radius
            lower = (r + 1) * piece_h + tab_radius
            crop_left = max(left, 0)
            crop_upper = max(upper, 0)
            crop_right = min(right, width)
            crop_lower = min(lower, height)
            region = Image.new("RGBA", (right - left, lower - upper), (0,0,0,0))
            region_part = img.crop((crop_left, crop_upper, crop_right, crop_lower))
            region.paste(region_part, (crop_left - left, crop_upper - upper))
            mask = masks[r][c]
            if mask.size != region.size:
                mask = mask.resize(region.size, resample=Image.NEAREST)
            mask_np = np.array(mask)
            # --- Make indents (holes) visible as true inward bites ---
            region_np = np.array(region)
            # Top edge
            if (r, c, 'top') in edge_types and edge_types[(r, c, 'top')] == -1:
                cx = tab_radius + piece_w // 2
                cy = tab_radius
                bbox = [cx - tab_radius, cy - tab_radius, cx + tab_radius, cy + tab_radius]
                # Set mask to 0 (transparent) in the bite region
                bite_mask = Image.new('L', region.size, 0)
                bite_draw = ImageDraw.Draw(bite_mask)
                bite_draw.pieslice(bbox, 180, 360, fill=255)
                bite_mask_np = np.array(bite_mask)
                mask_np[bite_mask_np == 255] = 0
                # Fill the bite with blue
                region_np[(bite_mask_np == 255)] = [0, 0, 255, 255]
            # Right edge
            if (r, c, 'right') in edge_types and edge_types[(r, c, 'right')] == -1:
                cx = tab_radius + piece_w
                cy = tab_radius + piece_h // 2
                bbox = [cx - tab_radius, cy - tab_radius, cx + tab_radius, cy + tab_radius]
                bite_mask = Image.new('L', region.size, 0)
                bite_draw = ImageDraw.Draw(bite_mask)
                bite_draw.pieslice(bbox, 270, 450, fill=255)
                bite_mask_np = np.array(bite_mask)
                mask_np[bite_mask_np == 255] = 0
                region_np[(bite_mask_np == 255)] = [0, 0, 255, 255]
            # Bottom edge
            if (r, c, 'bottom') in edge_types and edge_types[(r, c, 'bottom')] == -1:
                cx = tab_radius + piece_w // 2
                cy = tab_radius + piece_h
                bbox = [cx - tab_radius, cy - tab_radius, cx + tab_radius, cy + tab_radius]
                bite_mask = Image.new('L', region.size, 0)
                bite_draw = ImageDraw.Draw(bite_mask)
                bite_draw.pieslice(bbox, 0, 180, fill=255)
                bite_mask_np = np.array(bite_mask)
                mask_np[bite_mask_np == 255] = 0
                region_np[(bite_mask_np == 255)] = [0, 0, 255, 255]
            # Left edge
            if (r, c, 'left') in edge_types and edge_types[(r, c, 'left')] == -1:
                cx = tab_radius
                cy = tab_radius + piece_h // 2
                bbox = [cx - tab_radius, cy - tab_radius, cx + tab_radius, cy + tab_radius]
                bite_mask = Image.new('L', region.size, 0)
                bite_draw = ImageDraw.Draw(bite_mask)
                bite_draw.pieslice(bbox, 90, 270, fill=255)
                bite_mask_np = np.array(bite_mask)
                mask_np[bite_mask_np == 255] = 0
                region_np[(bite_mask_np == 255)] = [0, 0, 255, 255]
            # Apply the updated mask and region
            region = Image.fromarray(region_np)
            region.putalpha(Image.fromarray(mask_np))
            # Draw a red outline around the nonzero mask region for debugging
            outline_draw = ImageDraw.Draw(region)
            ys, xs = np.where(mask_np > 0)
            if len(xs) > 0 and len(ys) > 0:
                min_x, max_x = xs.min(), xs.max()
                min_y, max_y = ys.min(), ys.max()
                outline_draw.rectangle([min_x, min_y, max_x, max_y], outline=(255,0,0,255), width=2)
            region.save(os.path.join(output_dir, f"piece_{r*n_cols+c:02d}.png"))
            # For overlap check, only count the core rectangle (no padding)
            core_x0 = tab_radius
            core_y0 = tab_radius
            core_x1 = core_x0 + piece_w
            core_y1 = core_y0 + piece_h
            mask_core = mask_np[core_y0:core_y1, core_x0:core_x1]
            img_x0 = c * piece_w
            img_y0 = r * piece_h
            img_x1 = img_x0 + piece_w
            img_y1 = img_y0 + piece_h
            all_masks[img_y0:img_y1, img_x0:img_x1] += (mask_core > 0).astype(np.uint8)
    max_overlap = np.max(all_masks)
    if max_overlap > 1:
        print(f"WARNING: Overlap detected! Max overlap at any pixel: {max_overlap}")
        overlap_coords = np.argwhere(all_masks > 1)
        print(f"Overlap pixel coordinates (up to 20 shown): {overlap_coords[:20]}")
        vis = (np.clip(all_masks, 0, 2) * 127).astype(np.uint8)
        Image.fromarray(vis).save('overlap_debug.png')
        print("Saved overlap_debug.png for visual inspection.")
    else:
        print("No overlap detected. All pixels uniquely assigned.")
    print(f"Saved {n_rows*n_cols} jigsaw pieces to {output_dir}/")

def main():
    if len(sys.argv) < 2:
        print("Usage: python shatter2.py <image_path> [output_dir]")
        return
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "pieces_jigsaw"
    shatter2(image_path, 5, 10, output_dir)

if __name__ == "__main__":
    main() 