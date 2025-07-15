import numpy as np
from scipy.spatial import Voronoi
from scipy.ndimage import distance_transform_edt
from skimage.draw import polygon2mask
from PIL import Image
import os
import sys
from sklearn.cluster import KMeans

def voronoi_full_coverage(image_path, n_pieces=50, output_dir="pieces", seed=42, lloyd_iter=10):
    np.random.seed(seed)
    img = np.array(Image.open(image_path).convert("RGBA"))
    height, width = img.shape[:2]
    os.makedirs(output_dir, exist_ok=True)
    # Lloyd's relaxation for well-spaced seeds
    points = np.column_stack([
        np.random.uniform(0, width, n_pieces),
        np.random.uniform(0, height, n_pieces)
    ])
    for _ in range(lloyd_iter):
        vor = Voronoi(points)
        regions, vertices = voronoi_finite_polygons_2d(vor)
        new_points = []
        for region in regions:
            polygon_vertices = vertices[region]
            mask = polygon2mask((height, width), polygon_vertices)
            if np.sum(mask) == 0:
                new_points.append(points[len(new_points)])
                continue
            yx = np.argwhere(mask)
            centroid = yx.mean(axis=0)[::-1]
            cx = np.clip(centroid[0], 0, width-1)
            cy = np.clip(centroid[1], 0, height-1)
            new_points.append([cx, cy])
        points = np.array(new_points)
    vor = Voronoi(points)
    regions, vertices = voronoi_finite_polygons_2d(vor)
    # Create initial label map
    label_map = np.full((height, width), -1, dtype=int)
    for i, region in enumerate(regions):
        polygon_vertices = vertices[region]
        mask = polygon2mask((height, width), polygon_vertices)
        label_map[mask] = i
    # Fill any gaps by assigning to nearest region
    mask_uncovered = (label_map == -1)
    if np.any(mask_uncovered):
        dist, inds = distance_transform_edt(mask_uncovered, return_indices=True)
        label_map[mask_uncovered] = label_map[inds[0][mask_uncovered], inds[1][mask_uncovered]]
    # Relabel to ensure consecutive labels
    unique = np.unique(label_map)
    mapping = {old: new for new, old in enumerate(unique)}
    for old, new in mapping.items():
        label_map[label_map == old] = new
    # If fewer than n_pieces, split largest regions
    while len(np.unique(label_map)) < n_pieces:
        unique, counts = np.unique(label_map, return_counts=True)
        largest_label = unique[np.argmax(counts)]
        coords = np.argwhere(label_map == largest_label)
        if len(coords) < 2:
            break  # Can't split further
        kmeans = KMeans(n_clusters=2, random_state=seed)
        cluster_labels = kmeans.fit_predict(coords)
        new_label = max(label_map.max() + 1, n_pieces-1)
        label_map[tuple(coords[cluster_labels == 1].T)] = new_label
    # Relabel to 0..n_pieces-1
    unique = np.unique(label_map)
    mapping = {old: new for new, old in enumerate(unique)}
    for old, new in mapping.items():
        label_map[label_map == old] = new
    # Save each region as a piece
    for i in range(n_pieces):
        mask = (label_map == i)
        piece = np.zeros_like(img)
        for c in range(4):
            piece[..., c] = img[..., c] * mask.astype(img.dtype)
        piece_img = Image.fromarray(piece)
        piece_img.save(os.path.join(output_dir, f"piece_{i:02d}.png"))
    print(f"Saved {n_pieces} Voronoi pieces with full coverage to {output_dir}/")

# Helper for finite polygons
from scipy.spatial import Voronoi

def voronoi_finite_polygons_2d(vor, radius=None):
    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")
    new_regions = []
    new_vertices = vor.vertices.tolist()
    center = vor.points.mean(axis=0)
    if radius is None:
        radius = np.ptp(vor.points, axis=0).max() * 2
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]
        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]
        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0 and v2 < 0:
                t = vor.points[p2] - vor.points[p1]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])
                midpoint = vor.points[[p1, p2]].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[v1] + direction * radius
                new_vertices.append(far_point.tolist())
                new_region.append(len(new_vertices) - 1)
        new_regions.append(new_region)
    return new_regions, np.asarray(new_vertices)


def main():
    if len(sys.argv) < 2:
        print("Usage: python shatter.py <image_path> [output_dir] [n_pieces]")
        return
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "pieces"
    n_pieces = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    voronoi_full_coverage(image_path, n_pieces, output_dir)

if __name__ == "__main__":
    main() 