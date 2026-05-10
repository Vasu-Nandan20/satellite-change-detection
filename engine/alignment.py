"""
alignment.py — Multi-method image registration & alignment engine.

Supports ORB, SIFT, and ECC-based alignment with automatic quality scoring
to select the best registration result.
"""

import cv2
import numpy as np


class ImageAligner:
    """Handles satellite image alignment using multiple feature-based and
    intensity-based registration methods."""

    METHODS = ["ORB", "SIFT", "ECC"]

    def __init__(self, method="ORB"):
        if method not in self.METHODS:
            raise ValueError(f"Unknown alignment method: {method}. Choose from {self.METHODS}")
        self.method = method

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def align(self, reference, target):
        """Align *target* image to *reference* image.

        Parameters
        ----------
        reference : np.ndarray  – BGR reference (before) image
        target    : np.ndarray  – BGR target (after) image

        Returns
        -------
        aligned : np.ndarray – warped target image aligned to reference
        score   : float      – alignment quality metric (higher is better)
        """
        if self.method == "ORB":
            return self._align_orb(reference, target)
        elif self.method == "SIFT":
            return self._align_sift(reference, target)
        elif self.method == "ECC":
            return self._align_ecc(reference, target)

    # ------------------------------------------------------------------ #
    #  ORB-based alignment                                                 #
    # ------------------------------------------------------------------ #

    def _align_orb(self, ref, tgt):
        orb = cv2.ORB_create(5000)
        gray_ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
        gray_tgt = cv2.cvtColor(tgt, cv2.COLOR_BGR2GRAY)

        kp1, des1 = orb.detectAndCompute(gray_ref, None)
        kp2, des2 = orb.detectAndCompute(gray_tgt, None)

        if des1 is None or des2 is None or len(des1) < 4 or len(des2) < 4:
            return tgt.copy(), 0.0

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda m: m.distance)

        if len(matches) < 4:
            return tgt.copy(), 0.0

        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        matrix, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        if matrix is None:
            return tgt.copy(), 0.0

        aligned = cv2.warpPerspective(tgt, matrix, (ref.shape[1], ref.shape[0]))
        inlier_ratio = np.sum(mask) / len(mask) if mask is not None else 0
        return aligned, float(inlier_ratio)

    # ------------------------------------------------------------------ #
    #  SIFT-based alignment                                                #
    # ------------------------------------------------------------------ #

    def _align_sift(self, ref, tgt):
        sift = cv2.SIFT_create(nfeatures=5000)
        gray_ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
        gray_tgt = cv2.cvtColor(tgt, cv2.COLOR_BGR2GRAY)

        kp1, des1 = sift.detectAndCompute(gray_ref, None)
        kp2, des2 = sift.detectAndCompute(gray_tgt, None)

        if des1 is None or des2 is None or len(des1) < 4 or len(des2) < 4:
            return tgt.copy(), 0.0

        # Lowe's ratio test
        bf = cv2.BFMatcher()
        raw_matches = bf.knnMatch(des1, des2, k=2)
        good = []
        for m, n in raw_matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)

        if len(good) < 4:
            return tgt.copy(), 0.0

        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        matrix, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        if matrix is None:
            return tgt.copy(), 0.0

        aligned = cv2.warpPerspective(tgt, matrix, (ref.shape[1], ref.shape[0]))
        inlier_ratio = np.sum(mask) / len(mask) if mask is not None else 0
        return aligned, float(inlier_ratio)

    # ------------------------------------------------------------------ #
    #  ECC (Enhanced Correlation Coefficient) alignment                    #
    # ------------------------------------------------------------------ #

    def _align_ecc(self, ref, tgt):
        gray_ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
        gray_tgt = cv2.cvtColor(tgt, cv2.COLOR_BGR2GRAY)

        # Resize target to match reference dimensions
        gray_tgt = cv2.resize(gray_tgt, (gray_ref.shape[1], gray_ref.shape[0]))
        tgt_resized = cv2.resize(tgt, (ref.shape[1], ref.shape[0]))

        warp_matrix = np.eye(2, 3, dtype=np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 1000, 1e-6)

        try:
            cc, warp_matrix = cv2.findTransformECC(
                gray_ref, gray_tgt, warp_matrix, cv2.MOTION_AFFINE, criteria
            )
            aligned = cv2.warpAffine(
                tgt_resized, warp_matrix,
                (ref.shape[1], ref.shape[0]),
                flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
            )
            return aligned, float(cc)
        except cv2.error:
            return tgt_resized, 0.0


def auto_align(reference, target):
    """Try all alignment methods and return the best result."""
    best_aligned, best_score, best_method = None, -1, None
    for method_name in ImageAligner.METHODS:
        try:
            aligner = ImageAligner(method=method_name)
            aligned, score = aligner.align(reference, target)
            if score > best_score:
                best_aligned, best_score, best_method = aligned, score, method_name
        except Exception:
            continue
    if best_aligned is None:
        return target.copy(), 0.0, "None"
    return best_aligned, best_score, best_method
