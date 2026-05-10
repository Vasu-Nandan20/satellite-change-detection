"""
analyzer.py — Statistics computation and heatmap generation.

Computes change metrics, generates heatmap overlays, and provides
grid-based density analysis for detected changes.
"""

import cv2
import numpy as np
from datetime import datetime


class ChangeAnalyzer:
    """Compute statistics and generate visualizations from detection results."""

    def __init__(self, img_shape, contours, classifications, mask, raw_diff):
        self.img_h, self.img_w = img_shape[:2]
        self.contours = contours
        self.classifications = classifications
        self.mask = mask
        self.raw_diff = raw_diff

    # ------------------------------------------------------------------ #
    #  Summary statistics                                                  #
    # ------------------------------------------------------------------ #

    def compute_summary(self):
        """Return a summary dict of the analysis."""
        total_pixels = self.img_h * self.img_w
        changed_pixels = int(np.sum(self.mask > 0))
        change_pct = (changed_pixels / total_pixels) * 100 if total_pixels > 0 else 0

        areas = [c["area"] for c in self.classifications]

        type_counts = {}
        for c in self.classifications:
            t = c["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        avg_confidence = (
            np.mean([c["confidence"] for c in self.classifications])
            if self.classifications else 0
        )

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_changes": len(self.classifications),
            "changed_pixels": changed_pixels,
            "total_pixels": total_pixels,
            "change_percentage": round(change_pct, 2),
            "avg_change_area": round(np.mean(areas), 1) if areas else 0,
            "max_change_area": max(areas) if areas else 0,
            "min_change_area": min(areas) if areas else 0,
            "type_breakdown": type_counts,
            "avg_confidence": round(float(avg_confidence), 2),
        }

    # ------------------------------------------------------------------ #
    #  Heatmap generation                                                  #
    # ------------------------------------------------------------------ #

    def generate_heatmap(self, base_image):
        """Generate a colorful heatmap overlay on the base image."""
        # Normalize raw_diff to 0-255
        heat = (self.raw_diff * 255).astype(np.uint8)
        heat = cv2.GaussianBlur(heat, (21, 21), 0)
        heatmap_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)

        # Blend with base image
        overlay = cv2.addWeighted(base_image, 0.6, heatmap_color, 0.4, 0)
        return overlay

    # ------------------------------------------------------------------ #
    #  Annotated result image                                              #
    # ------------------------------------------------------------------ #

    def generate_annotated_image(self, base_image):
        """Draw classified bounding boxes with labels on the image."""
        annotated = base_image.copy()
        for cls in self.classifications:
            x, y, w, h = cls["bbox"]
            color = cls["color"]
            label = f"{cls['type']} ({cls['confidence']:.0%})"

            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

            # Label background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.4
            thickness = 1
            (tw, th), _ = cv2.getTextSize(label, font, font_scale, thickness)
            cv2.rectangle(annotated, (x, y - th - 6), (x + tw + 4, y), color, -1)
            cv2.putText(annotated, label, (x + 2, y - 4), font, font_scale,
                        (255, 255, 255), thickness, cv2.LINE_AA)

        # Timestamp overlay
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated, f"Analysis: {ts}", (10, annotated.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        return annotated

    # ------------------------------------------------------------------ #
    #  Grid density map                                                    #
    # ------------------------------------------------------------------ #

    def compute_grid_density(self, grid_rows=8, grid_cols=8):
        """Divide the image into a grid and compute change density per cell.

        Returns
        -------
        density : np.ndarray – shape (grid_rows, grid_cols), values 0.0-1.0
        """
        cell_h = self.img_h // grid_rows
        cell_w = self.img_w // grid_cols

        density = np.zeros((grid_rows, grid_cols), dtype=np.float32)
        for r in range(grid_rows):
            for c in range(grid_cols):
                y1, y2 = r * cell_h, (r + 1) * cell_h
                x1, x2 = c * cell_w, (c + 1) * cell_w
                cell = self.mask[y1:y2, x1:x2]
                cell_total = cell.size
                cell_changed = np.sum(cell > 0)
                density[r, c] = cell_changed / cell_total if cell_total > 0 else 0

        return density

    # ------------------------------------------------------------------ #
    #  Size classification                                                 #
    # ------------------------------------------------------------------ #

    def classify_by_size(self):
        """Classify changes into Small / Medium / Large buckets."""
        small, medium, large = [], [], []
        for cls in self.classifications:
            a = cls["area"]
            if a < 500:
                small.append(cls)
            elif a < 5000:
                medium.append(cls)
            else:
                large.append(cls)
        return {"Small": small, "Medium": medium, "Large": large}
