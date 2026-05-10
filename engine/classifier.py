"""
classifier.py — Change-type classification engine.

Uses contour geometry features and color analysis to classify detected changes
into categories: Construction, Vegetation, Water, Demolition, Other.
"""

import cv2
import numpy as np

try:
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


# Classification labels and color mapping (BGR)
CHANGE_TYPES = {
    "Construction":      (0, 100, 255),   # Orange
    "Vegetation Change": (0, 200, 0),     # Green
    "Water Change":      (255, 180, 0),   # Cyan-ish blue
    "Demolition":        (0, 0, 255),     # Red
    "Other":             (200, 200, 0),   # Yellow-ish
}

CHANGE_TYPE_LIST = list(CHANGE_TYPES.keys())


class ChangeClassifier:
    """Classify detected change regions by type."""

    def __init__(self):
        self.labels = CHANGE_TYPE_LIST

    def classify_contours(self, contours, img_before, img_after):
        """
        Classify each contour into a change type.

        Returns
        -------
        classifications : list[dict]
            Each dict has: 'bbox', 'area', 'type', 'color', 'confidence', 'contour'
        """
        if not contours:
            return []

        results = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            aspect_ratio = w / max(h, 1)

            # Extract ROI from both images
            roi_before = img_before[y:y+h, x:x+w]
            roi_after = img_after[y:y+h, x:x+w]

            if roi_before.size == 0 or roi_after.size == 0:
                change_type = "Other"
            else:
                change_type = self._classify_single(roi_before, roi_after, area, aspect_ratio)

            color = CHANGE_TYPES[change_type]
            confidence = self._compute_confidence(cnt, img_before, img_after)

            results.append({
                "bbox": (x, y, w, h),
                "area": area,
                "type": change_type,
                "color": color,
                "confidence": confidence,
                "contour": cnt,
            })

        return results

    def _classify_single(self, roi_before, roi_after, area, aspect_ratio):
        """Rule-based + color analysis classification."""
        # Convert to HSV for color analysis
        hsv_before = cv2.cvtColor(roi_before, cv2.COLOR_BGR2HSV)
        hsv_after = cv2.cvtColor(roi_after, cv2.COLOR_BGR2HSV)

        mean_h_before = np.mean(hsv_before[:, :, 0])
        mean_s_before = np.mean(hsv_before[:, :, 1])
        mean_v_before = np.mean(hsv_before[:, :, 2])

        mean_h_after = np.mean(hsv_after[:, :, 0])
        mean_s_after = np.mean(hsv_after[:, :, 1])
        mean_v_after = np.mean(hsv_after[:, :, 2])

        # Vegetation detection: green hue range (35-85)
        green_before = 35 <= mean_h_before <= 85 and mean_s_before > 40
        green_after = 35 <= mean_h_after <= 85 and mean_s_after > 40

        if green_before != green_after:
            return "Vegetation Change"

        # Water detection: blue hue range (90-130)
        blue_before = 90 <= mean_h_before <= 130 and mean_s_before > 30
        blue_after = 90 <= mean_h_after <= 130 and mean_s_after > 30

        if blue_before != blue_after:
            return "Water Change"

        # Brightness analysis for construction vs demolition
        brightness_change = mean_v_after - mean_v_before

        if brightness_change > 20:
            return "Construction"  # New structures tend to be brighter
        elif brightness_change < -20:
            return "Demolition"

        # Large regular-shaped changes suggest construction
        if area > 2000 and 0.5 < aspect_ratio < 2.0:
            return "Construction"

        return "Other"

    def _compute_confidence(self, contour, img_before, img_after):
        """Compute a confidence score (0.0-1.0) for a detected change."""
        x, y, w, h = cv2.boundingRect(contour)
        roi_b = img_before[y:y+h, x:x+w]
        roi_a = img_after[y:y+h, x:x+w]

        if roi_b.size == 0 or roi_a.size == 0:
            return 0.5

        diff = cv2.absdiff(roi_b, roi_a)
        mean_diff = np.mean(diff) / 255.0
        # Scale to 0.3-1.0 range
        confidence = min(1.0, 0.3 + mean_diff * 2.0)
        return round(confidence, 2)
