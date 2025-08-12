import numpy as np
from scipy.spatial import Voronoi
from scipy.ndimage import distance_transform_edt
from skimage.draw import polygon2mask
from PIL import Image
import os
import sys
from sklearn.cluster import KMeans
import time
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def save_piece_optimized(args):
    i, img, label_map, output_dir = args
    mask = (label_map == i)
    if not np.any(mask):
        piece = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.uint8)
    else:
        piece = np.zeros_like(img)
        piece[mask] = img[mask]
    piece_img = Image.fromarray(piece)
    piece_img.save(os.path.join(output_dir, f"piece_{i:02d}.png"))

def centroid_and_mask(args):
    region, vertices, height, width, points, idx = args
    polygon_vertices = vertices[region]
    mask = polygon2mask((height, width), polygon_vertices)
    if np.sum(mask) == 0:
        return points[idx], mask
    yx = np.argwhere(mask)
    centroid = yx.mean(axis=0)[::-1]
    cx = np.clip(centroid[0], 0, width-1)
    cy = np.clip(centroid[1], 0, height-1)
    return [cx, cy], mask

def voronoi_full_coverage(image_path, n_pieces=50, output_dir="pieces", seed=42, lloyd_iter=0):
    np.random.seed(seed)
    t0 = time.time()
    img = np.array(Image.open(image_path).convert("RGBA"))
    height, width = img.shape[:2]
    os.makedirs(output_dir, exist_ok=True)
    
    grid_size = int(np.ceil(np.sqrt(n_pieces)))
    x_grid = np.linspace(width * 0.1, width * 0.9, grid_size)
    y_grid = np.linspace(height * 0.1, height * 0.9, grid_size)
    xx, yy = np.meshgrid(x_grid, y_grid)
    points = np.column_stack([xx.ravel(), yy.ravel()])
    
    jitter = np.random.uniform(-width * 0.15, width * 0.15, (len(points), 2))
    points = points + jitter
    
    points = points[:n_pieces]
    
    for iter_num in range(lloyd_iter):
        vor = Voronoi(points)
        regions, vertices = voronoi_finite_polygons_2d(vor)
        
        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            results = list(executor.map(
                centroid_and_mask,
                [(region, vertices, height, width, points, idx) for idx, region in enumerate(regions)]
            ))
        new_points = [r[0] for r in results]
        points = np.array(new_points)
    
    vor = Voronoi(points)
    regions, vertices = voronoi_finite_polygons_2d(vor)
    
    label_map = np.full((height, width), -1, dtype=int)
    
    def process_region(args):
        i, region = args
        polygon_vertices = vertices[region]
        mask = polygon2mask((height, width), polygon_vertices)
        return i, mask
    
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results = list(executor.map(process_region, [(i, region) for i, region in enumerate(regions)]))
    
    for i, mask in results:
        label_map[mask] = i
    
    mask_uncovered = (label_map == -1)
    if np.any(mask_uncovered):
        dist, inds = distance_transform_edt(mask_uncovered, return_indices=True)
        label_map[mask_uncovered] = label_map[inds[0][mask_uncovered], inds[1][mask_uncovered]]
    
    unique_labels = np.unique(label_map)
    if len(unique_labels) > n_pieces:
        selected_labels = unique_labels[:n_pieces]
        new_label_map = np.full_like(label_map, -1)
        for new_idx, old_label in enumerate(selected_labels):
            new_label_map[label_map == old_label] = new_idx
        label_map = new_label_map
    elif len(unique_labels) < n_pieces:
        while len(np.unique(label_map)) < n_pieces:
            unique, counts = np.unique(label_map, return_counts=True)
            largest_label = unique[np.argmax(counts)]
            coords = np.argwhere(label_map == largest_label)
            if len(coords) < 2:
                break
            kmeans = KMeans(n_clusters=2, random_state=seed, n_init=1)
            cluster_labels = kmeans.fit_predict(coords)
            new_label = max(label_map.max() + 1, n_pieces-1)
            label_map[tuple(coords[cluster_labels == 1].T)] = new_label
    
    unique = np.unique(label_map)
    mapping = {old: new for new, old in enumerate(unique)}
    for old, new in mapping.items():
        label_map[label_map == old] = new
    
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [
            executor.submit(save_piece_optimized, (i, img, label_map, output_dir))
            for i in range(n_pieces)
        ]
        for f in futures:
            f.result()
    
    print(f"Total shatter time: {time.time() - t0:.2f}s")

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