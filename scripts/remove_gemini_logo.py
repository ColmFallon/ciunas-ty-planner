#!/opt/anaconda3/bin/python3
from __future__ import annotations

from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image


def inpaint_diffusion_region(region: np.ndarray, region_mask: np.ndarray, iterations: int = 140) -> np.ndarray:
    """Diffuse surrounding colour/texture into masked area via neighbour averaging."""
    out = region.astype(np.float32).copy()
    h, w = region_mask.shape
    known = ~region_mask

    for _ in range(iterations):
        padded = np.pad(out, ((1, 1), (1, 1), (0, 0)), mode='edge')
        known_p = np.pad(known, ((1, 1), (1, 1)), mode='edge')

        neigh_sum = np.zeros_like(out)
        neigh_count = np.zeros((h, w), dtype=np.float32)

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                y0 = 1 + dy
                x0 = 1 + dx
                n = padded[y0:y0 + h, x0:x0 + w, :]
                v = known_p[y0:y0 + h, x0:x0 + w].astype(np.float32)
                neigh_sum += n * v[..., None]
                neigh_count += v

        fillable = region_mask & (neigh_count > 0)
        if not np.any(fillable):
            break

        out[fillable] = neigh_sum[fillable] / neigh_count[fillable, None]
        # Propagate the fill front inwards so the full masked area gets replaced.
        known[fillable] = True

    return np.clip(out, 0, 255).astype(np.uint8)


def main() -> None:
    root = Path('/Users/Colm/Documents/Ciunas website')
    src = root / 'Book assets/AI/cover.png'
    dst = root / 'assets/ai_cover_background_clean.png'

    arr = np.array(Image.open(src).convert('RGB'))
    h, w, _ = arr.shape

    # Bottom-right detection rectangle (~12% x ~12%).
    x0 = int(w * 0.88)
    y0 = int(h * 0.88)

    # Detect bright logo pixels within that corner rectangle, then inpaint only that shape.
    roi = arr[y0:h, x0:w, :]
    gray = (0.299 * roi[:, :, 0] + 0.587 * roi[:, :, 1] + 0.114 * roi[:, :, 2])
    yy, xx = np.indices(gray.shape)
    # Focus on the lower-right sub-area to avoid catching the bright horizon band.
    in_lower_right = (yy > gray.shape[0] * 0.40) & (xx > gray.shape[1] * 0.25)
    candidates = (gray > 130.0) & in_lower_right

    rh_roi, rw_roi = candidates.shape
    visited = np.zeros_like(candidates, dtype=bool)
    components: list[tuple[int, tuple[int, int, int, int], list[tuple[int, int]]]] = []

    for yy in range(rh_roi):
        for xx in range(rw_roi):
            if not candidates[yy, xx] or visited[yy, xx]:
                continue
            q = deque([(yy, xx)])
            visited[yy, xx] = True
            pts: list[tuple[int, int]] = []
            y_min = y_max = yy
            x_min = x_max = xx
            while q:
                cy, cx = q.popleft()
                pts.append((cy, cx))
                y_min = min(y_min, cy)
                y_max = max(y_max, cy)
                x_min = min(x_min, cx)
                x_max = max(x_max, cx)
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if ny < 0 or ny >= rh_roi or nx < 0 or nx >= rw_roi:
                        continue
                    if visited[ny, nx] or not candidates[ny, nx]:
                        continue
                    visited[ny, nx] = True
                    q.append((ny, nx))
            components.append((len(pts), (y_min, y_max, x_min, x_max), pts))

    logo_mask_roi = np.zeros_like(candidates, dtype=bool)
    if components:
        # Prefer the component nearest bottom-right with meaningful size.
        def score(comp: tuple[int, tuple[int, int, int, int], list[tuple[int, int]]]) -> tuple[float, int]:
            size, (_ymin, ymax, _xmin, xmax), _pts = comp
            dist = ((rh_roi - 1 - ymax) ** 2 + (rw_roi - 1 - xmax) ** 2) ** 0.5
            return (dist, -size)

        components.sort(key=score)
        best = next((c for c in components if c[0] >= 20), components[0])
        _, _, pts = best
        for py, px in pts:
            logo_mask_roi[py, px] = True
    else:
        # Fallback: small corner patch if detection misses.
        logo_mask_roi[max(0, rh_roi - 72):rh_roi, max(0, rw_roi - 72):rw_roi] = True

    # Dilate mask to include anti-aliased edges.
    for _ in range(7):
        expanded = logo_mask_roi.copy()
        expanded[1:, :] |= logo_mask_roi[:-1, :]
        expanded[:-1, :] |= logo_mask_roi[1:, :]
        expanded[:, 1:] |= logo_mask_roi[:, :-1]
        expanded[:, :-1] |= logo_mask_roi[:, 1:]
        logo_mask_roi = expanded

    ys, xs = np.where(logo_mask_roi)
    if ys.size == 0:
        raise RuntimeError('Logo mask detection failed.')

    y_min = int(max(0, ys.min() - 48))
    y_max = int(min(rh_roi - 1, ys.max() + 48))
    x_min = int(max(0, xs.min() - 48))
    x_max = int(min(rw_roi - 1, xs.max() + 48))

    # Process only local work area around the detected logo for natural blending.
    wy0 = y0 + y_min
    wy1 = y0 + y_max + 1
    wx0 = x0 + x_min
    wx1 = x0 + x_max + 1

    region = arr[wy0:wy1, wx0:wx1, :].copy()
    region_mask = logo_mask_roi[y_min:y_max + 1, x_min:x_max + 1]

    cleaned_region = inpaint_diffusion_region(region, region_mask, iterations=140)
    arr[wy0:wy1, wx0:wx1, :] = cleaned_region

    dst.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).save(dst)

    print(f'Input:  {src}')
    print(f'Output: {dst}')
    print(f'Size:   {w}x{h}')
    print(f'Detect region: x={x0}, y={y0}, w={w-x0}, h={h-y0}')


if __name__ == '__main__':
    main()
