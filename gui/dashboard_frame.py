"""
dashboard_frame.py — Dashboard / home screen with quick stats and recent activity.
"""

import customtkinter as ctk
import os
import csv
from datetime import datetime


class DashboardFrame(ctk.CTkFrame):
    """Welcome dashboard with stats overview and recent activity."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_hero()
        self._build_stats()
        self._build_activity()

    # ------------------------------------------------------------------ #
    #  Hero Section                                                        #
    # ------------------------------------------------------------------ #

    def _build_hero(self):
        hero = ctk.CTkFrame(self, corner_radius=15,
                            fg_color=("#1a73e8", "#0d47a1"))
        hero.grid(row=0, column=0, padx=25, pady=(25, 15), sticky="ew")

        ctk.CTkLabel(
            hero, text="🛰️  Welcome to SENTINEL",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white",
        ).pack(padx=30, pady=(25, 5), anchor="w")

        ctk.CTkLabel(
            hero,
            text="Advanced Satellite Image Change Detection System  •  Powered by OpenCV, SIFT, SSIM & ML Classification",
            font=ctk.CTkFont(size=13),
            text_color="#b3d4fc",
        ).pack(padx=30, pady=(0, 8), anchor="w")

        ctk.CTkLabel(
            hero,
            text="Select 'Detection' from the sidebar to begin analyzing satellite imagery.",
            font=ctk.CTkFont(size=12),
            text_color="#90caf9",
        ).pack(padx=30, pady=(0, 25), anchor="w")

    # ------------------------------------------------------------------ #
    #  Stats Cards                                                         #
    # ------------------------------------------------------------------ #

    def _build_stats(self):
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, padx=25, pady=5, sticky="ew")
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)

        # Read history for stats
        total_analyses, total_changes, last_date = self._read_history_stats()

        cards = [
            ("📷", "Total Analyses",   str(total_analyses), "#1a73e8"),
            ("🔍", "Changes Found",    str(total_changes),  "#e53935"),
            ("📅", "Last Analysis",    last_date,           "#34a853"),
            ("⚡", "Engine Status",    "Active",            "#fb8c00"),
        ]

        for i, (icon, title, value, color) in enumerate(cards):
            card = ctk.CTkFrame(stats_frame, corner_radius=12,
                                fg_color=("#ffffff", "#1e1e3a"),
                                border_width=1,
                                border_color=("#e0e0e0", "#2a2a4a"))
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")

            ctk.CTkLabel(card, text=icon,
                         font=ctk.CTkFont(size=28)).pack(padx=15, pady=(15, 5), anchor="w")
            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont(size=11),
                         text_color=("#888", "#999")).pack(padx=15, anchor="w")
            ctk.CTkLabel(card, text=value,
                         font=ctk.CTkFont(size=22, weight="bold"),
                         text_color=color).pack(padx=15, pady=(2, 15), anchor="w")

    # ------------------------------------------------------------------ #
    #  Recent Activity                                                     #
    # ------------------------------------------------------------------ #

    def _build_activity(self):
        activity_frame = ctk.CTkFrame(self, corner_radius=12,
                                       fg_color=("#ffffff", "#1e1e3a"),
                                       border_width=1,
                                       border_color=("#e0e0e0", "#2a2a4a"))
        activity_frame.grid(row=2, column=0, padx=25, pady=(15, 25), sticky="nsew")

        ctk.CTkLabel(
            activity_frame, text="📋  Recent Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(padx=20, pady=(15, 10), anchor="w")

        # Feature highlights
        features = [
            "🔹  Multi-method alignment: ORB, SIFT, ECC with auto-selection",
            "🔹  Advanced detection: Absolute Difference, SSIM, Combined modes",
            "🔹  AI Classification: Construction, Vegetation, Water, Demolition",
            "🔹  Heatmap visualization with density grid analysis",
            "🔹  Professional PDF & CSV report generation",
            "🔹  Interactive analytics with embedded charts",
            "🔹  Dark / Light theme support with modern UI",
            "🔹  Configurable sensitivity and minimum area filters",
        ]

        for feat in features:
            ctk.CTkLabel(
                activity_frame, text=feat,
                font=ctk.CTkFont(size=12),
                text_color=("#555", "#aaa"),
            ).pack(padx=25, pady=2, anchor="w")

        # Quick start button
        ctk.CTkButton(
            activity_frame,
            text="🚀  Start New Detection",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42, corner_radius=10,
            fg_color=("#1a73e8", "#1a73e8"),
            hover_color=("#1565c0", "#1565c0"),
            command=lambda: self.app.show_frame("detection") if self.app else None,
        ).pack(padx=20, pady=(15, 20), anchor="w")

    # ------------------------------------------------------------------ #
    #  History Stats Reader                                                #
    # ------------------------------------------------------------------ #

    def _read_history_stats(self):
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "change_log.csv")
        if not os.path.exists(csv_path):
            return 0, 0, "Never"

        try:
            timestamps = set()
            total_rows = 0
            with open(csv_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 5:
                        # Try to parse timestamp from first column
                        try:
                            datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                            timestamps.add(row[0])
                            total_rows += 1
                        except ValueError:
                            pass

            last_date = max(timestamps) if timestamps else "Never"
            if last_date != "Never":
                last_date = last_date[:10]  # Just the date part

            return len(timestamps), total_rows, last_date
        except Exception:
            return 0, 0, "Never"
