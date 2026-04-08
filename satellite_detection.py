import cv2
import numpy as np
from datetime import datetime
import csv
import os
from tkinter import Tk, filedialog, Button, Label

# ----------------- Utility Functions -----------------

def align_images(img1, img2):
    orb = cv2.ORB_create(5000)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    matrix, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
    aligned_img = cv2.warpPerspective(img2, matrix, (img1.shape[1], img1.shape[0]))
    return aligned_img

def detect_changes(img1, img2):
    diff = cv2.absdiff(img1, img2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5,5), np.uint8)
    clean_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, clean_mask

def overlay_timestamp(img):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(img, f"Time: {ts}", (10, img.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return ts

def log_to_csv(bounding_boxes, timestamp):
    file_exists = os.path.isfile("change_log.csv")
    with open("change_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "X", "Y", "Width", "Height"])
        for (x, y, w, h) in bounding_boxes:
            writer.writerow([timestamp, x, y, w, h])

# ----------------- GUI Functions -----------------

def select_image1():
    global img1_path
    img1_path = filedialog.askopenfilename(title="Select First Image")
    Label(root, text=f"Image 1: {os.path.basename(img1_path)}").pack()

def select_image2():
    global img2_path
    img2_path = filedialog.askopenfilename(title="Select Second Image")
    Label(root, text=f"Image 2: {os.path.basename(img2_path)}").pack()

def run_detection():
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    aligned_img2 = align_images(img1, img2)
    contours, mask = detect_changes(img1, aligned_img2)

    bounding_boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        bounding_boxes.append((x, y, w, h))
        cv2.rectangle(aligned_img2, (x, y), (x+w, y+h), (0, 0, 255), 2)

    timestamp = overlay_timestamp(aligned_img2)
    log_to_csv(bounding_boxes, timestamp)

    # Display outputs
    cv2.imshow("Before Image", img1)
    cv2.imshow("After Image with Detection", aligned_img2)
    cv2.imshow("Change Mask", mask)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ----------------- Main GUI -----------------

root = Tk()
root.title("Satellite Image Change Detection")

Button(root, text="Select First Image", command=select_image1,
       font=("Arial", 14), width=25, height=2).pack(pady=5)

Button(root, text="Select Second Image", command=select_image2,
       font=("Arial", 14), width=25, height=2).pack(pady=5)

Button(root, text="Run Detection", command=run_detection,
       font=("Arial", 14), width=25, height=2,
       bg="green", fg="white").pack(pady=10)

root.mainloop()