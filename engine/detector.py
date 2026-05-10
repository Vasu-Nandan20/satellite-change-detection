"""
detector.py — Multi-method change detection engine.

Supports Absolute Difference, SSIM-based, and Combined detection strategies
with configurable sensitivity and morphological cleaning.
"""

import cv2
import numpy as np

try:
    from skimage.metrics import structural_similarity as ssim
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False


class ChangeDetector:
    """Detects changes between two aligned satellite images."""

    METHODS = ["Absolute Difference", "SSIM", "Combined"]

    def __init__(self, method="Absolute Difference", sensitivity=50, min_area=100):
        """
        Parameters
        ----------
        method      : str   – detection algorithm
        sensitivity : int   – 1-100, higher = more sensitive (lower threshold)
        min_area    : int   – minimum contour area in pixels to keep
        """
        self.method = method
        self.sensitivity = max(1, min(100, sensitivity))
        self.min_area = max(1, min_area)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def detect(self, img_before, img_after):
        """
        Run change detection.

        Returns
        -------
        contours  : list[np.ndarray]  – filtered contour list
        mask      : np.ndarray        – binary change mask (uint8, 0/255)
        raw_diff  : np.ndarray        – raw difference map (grayscale float 0-1)
        """
        if self.method == "Absolute Difference":
            mask, raw_diff = self._detect_absdiff(img_before, img_after)
        elif self.method == "SSIM" and HAS_SKIMAGE:
            mask, raw_diff = self._detect_ssim(img_before, img_after)
        elif self.method == "Combined" and HAS_SKIMAGE:
            mask, raw_diff = self._detect_combined(img_before, img_after)
        else:
            mask, raw_diff = self._detect_absdiff(img_before, img_after)

        # Morphological cleaning
        mask = self._clean_mask(mask)

        # Find and filter contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [c for c in contours if cv2.contourArea(c) >= self.min_area]
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        return contours, mask, raw_diff

    # ------------------------------------------------------------------ #
    #  Absolute Difference                                                 #
    # ------------------------------------------------------------------ #

    def _detect_absdiff(self, before, after):
        diff = cv2.absdiff(before, after)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Map sensitivity 1-100 to threshold 250-5 (higher sensitivity = lower threshold)
        threshold = int(255 - (self.sensitivity / 100.0) * 245)
        threshold = max(5, min(250, threshold))

        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        raw_diff = gray.astype(np.float32) / 255.0
        return binary, raw_diff

    # ------------------------------------------------------------------ #
    #  SSIM-based detection                                                #
    # ------------------------------------------------------------------ #

    def _detect_ssim(self, before, after):
        gray_b = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
        gray_a = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

        score, diff = ssim(gray_b, gray_a, full=True)
        diff = (1.0 - diff)  # Invert: high values = big change
        diff = np.clip(diff, 0, 1)

        threshold = 1.0 - (self.sensitivity / 100.0) * 0.95
        threshold = max(0.05, min(0.95, threshold))

        binary = (diff > threshold).astype(np.uint8) * 255
        return binary, diff.astype(np.float32)

    # ------------------------------------------------------------------ #
    #  Combined (AbsDiff + SSIM)                                           #
    # ------------------------------------------------------------------ #

    def _detect_combined(self, before, after):
        mask_abs, raw_abs = self._detect_absdiff(before, after)
        mask_ssim, raw_ssim = self._detect_ssim(before, after)

        # Union of both masks
        combined_mask = cv2.bitwise_or(mask_abs, mask_ssim)
        combined_raw = np.maximum(raw_abs, raw_ssim)
        return combined_mask, combined_raw

    # ------------------------------------------------------------------ #
    #  Morphological cleaning                                              #
    # ------------------------------------------------------------------ #

    def _clean_mask(self, mask):
        kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        kernel_large = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

        # Remove small noise
        cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_small, iterations=2)
        # Fill small holes
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_large, iterations=2)
        return cleaned
