# 🌍 Satellite Image Change Detection

This project is a Python-based system that detects changes between two satellite images captured at different times using computer vision techniques.

## 🚀 Features
- Automatic image alignment using ORB feature matching
- Change detection using image differencing
- Noise removal using morphological operations
- Bounding boxes highlighting changed regions
- Change mask visualization
- Timestamp overlay on output image
- CSV (Excel-compatible) logging of change coordinates
- Simple and user-friendly Tkinter GUI

## 🛠️ Technologies Used
- Python
- OpenCV
- NumPy
- Tkinter

## ▶️ How to Run

1. Install dependencies:
pip install -r requirements.txt

2. Run the project:
python satellite_detection.py

## 📊 Output

- Before Image  
- After Image with detected changes  
- Change Mask (binary image)  
- CSV file containing:
  - Timestamp  
  - X, Y coordinates  
  - Width and Height of detected regions  

---

## 🎯 Applications

- Defence surveillance  
- Urban development monitoring  
- Disaster damage assessment  
- Environmental change tracking  

---

## ⚠️ Limitations

- Sensitive to lighting variations  
- Requires similar viewpoint images  
- Does not classify type of change (only detects changes)  

---

## 🚀 Future Improvements

- Real-time monitoring system  
- AI-based change classification  
- PDF report generation  
- GIS/Map integration  
