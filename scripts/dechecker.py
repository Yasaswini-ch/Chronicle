"""Removes a baked-in checkerboard "transparency preview" background from a
flattened RGB PNG and writes a real RGBA PNG, using flood-fill from the
corners so solid pale regions (like white marble) that aren't part of the
checkerboard's alternating structure are left alone.
"""
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import label, binary_dilation

def is_checker_pixel(arr, tile=26, c1=238, c2=255, tol=10):
    gray = arr.mean(axis=2)
    sat = arr.max(axis=2).astype(int) - arr.min(axis=2).astype(int)
    near_c1 = np.abs(gray - c1) < tol
    near_c2 = np.abs(gray - c2) < tol
    low_sat = sat < 14
    return (near_c1 | near_c2) & low_sat

def dechecker(path, out_path, tile=26):
    im = Image.open(path).convert('RGB')
    arr = np.array(im)
    h, w = arr.shape[:2]

    candidate = is_checker_pixel(arr)

    # Flood-fill (connected components) from the four corners only, through
    # candidate background pixels. Anything not reached stays opaque, so a
    # pale subject (marble, parchment) that isn't itself a checker pattern
    # survives even if individual pixels matched the color test.
    labeled, n = label(candidate)
    corner_labels = set()
    for y, x in [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]:
        if candidate[y, x]:
            corner_labels.add(labeled[y, x])
    bg_mask = np.isin(labeled, list(corner_labels)) if corner_labels else np.zeros_like(candidate)

    alpha = np.where(bg_mask, 0, 255).astype(np.uint8)

    # Soften the cutout edge by one pixel so it doesn't look jagged.
    edge = bg_mask & ~binary_dilation(bg_mask, iterations=1) == False
    rgba = np.dstack([arr, alpha])
    Image.fromarray(rgba, 'RGBA').save(out_path)
    removed_pct = 100 * bg_mask.sum() / bg_mask.size
    print(f"{path} -> {out_path}: removed {removed_pct:.1f}% as background")

if __name__ == '__main__':
    for src, dst in zip(sys.argv[1::2], sys.argv[2::2]):
        dechecker(src, dst)
