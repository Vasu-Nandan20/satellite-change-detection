"""
app.py — SENTINEL: Satellite Change Detection System
=====================================================

Entry point for the advanced satellite image change detection application.

Features:
  • Multi-method image alignment (ORB, SIFT, ECC)
  • Advanced change detection (Absolute Diff, SSIM, Combined)
  • AI-powered change classification (Construction, Vegetation, Water, Demolition)
  • Heatmap visualization and density grid analysis
  • Interactive analytics with embedded matplotlib charts
  • Professional PDF & CSV report generation
  • Modern dark-themed GUI with CustomTkinter

Usage:
    python app.py
"""

import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from gui.app_window import AppWindow
from gui.dashboard_frame import DashboardFrame
from gui.detection_frame import DetectionFrame
from gui.analytics_frame import AnalyticsFrame
from gui.history_frame import HistoryFrame
from gui.settings_frame import SettingsFrame


def main():
    """Launch the SENTINEL application."""
    # Set appearance before creating window
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create main window
    app = AppWindow()

    # Register all frames
    app.register_frame("dashboard", DashboardFrame, app=app)
    app.register_frame("detection", DetectionFrame, app=app)
    app.register_frame("analytics", AnalyticsFrame, app=app)
    app.register_frame("history",   HistoryFrame,   app=app)
    app.register_frame("settings",  SettingsFrame,  app=app)

    # Show dashboard by default
    app.show_frame("dashboard")
    app.set_status("System Ready")

    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Run application
    app.mainloop()


if __name__ == "__main__":
    main()
