"""
image_utils.py — Common image loading, resizing, and conversion helpers.
"""

import cv2
import numpy as np
from PIL import Image, ImageTk


def load_image(path):
    """Load an image from disk. Returns BGR numpy array or None."""
    img = cv2.imread(path)
    return img


def resize_to_match(img, target_shape):
    """Resize img to match target_shape (h, w)."""
    h, w = target_shape[:2]
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)


def cv2_to_pil(img_bgr):
    """Convert OpenCV BGR image to PIL RGB Image."""
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def cv2_to_tk(img_bgr, max_size=None):
    """Convert OpenCV BGR image to tkinter-compatible PhotoImage.

    Parameters
    ----------
    img_bgr  : np.ndarray
    max_size : tuple (max_w, max_h) – resize to fit within this box

    Returns
    -------
    ImageTk.PhotoImage
    """
    pil_img = cv2_to_pil(img_bgr)
    if max_size:
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(pil_img)


def create_side_by_side(img1, img2, gap=10):
    """Create a side-by-side composite of two images with a gap."""
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    max_h = max(h1, h2)

    # Resize both to same height
    if h1 != max_h:
        scale = max_h / h1
        img1 = cv2.resize(img1, (int(w1 * scale), max_h))
    if h2 != max_h:
        scale = max_h / h2
        img2 = cv2.resize(img2, (int(w2 * scale), max_h))

    w1 = img1.shape[1]
    w2 = img2.shape[1]
    canvas = np.zeros((max_h, w1 + gap + w2, 3), dtype=np.uint8)
    canvas[:, :w1] = img1
    canvas[:, w1 + gap:] = img2
    return canvas


def create_thumbnail(img_bgr, size=(200, 200)):
    """Create a square thumbnail with aspect-ratio preservation."""
    pil = cv2_to_pil(img_bgr)
    pil.thumbnail(size, Image.Resampling.LANCZOS)
    return pil
