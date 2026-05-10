"""
history_frame.py — Past detection sessions viewer.

Reads from change_log.csv and displays in a scrollable table with
date filtering and session grouping.
"""

import customtkinter as ctk
import csv
import os
from datetime import datetime


class HistoryFrame(ctk.CTkFrame):
    """View past detection sessions from the CSV log."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_table()

    def _build_header(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0,
                               fg_color=("#f8f9fa", "#12122a"))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="📋  Detection History",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=25, pady=15, sticky="w")

        ctk.CTkButton(
            header, text="🔄 Refresh",
            font=ctk.CTkFont(size=12), height=34, corner_radius=8,
            fg_color=("#1a73e8", "#1a73e8"),
            hover_color=("#1565c0", "#1565c0"),
            command=self._load_data,
        ).grid(row=0, column=2, padx=25, pady=15, sticky="e")

    def _build_table(self):
        table_container = ctk.CTkFrame(self, corner_radius=12,
                                        fg_color=("#ffffff", "#1e1e3a"),
                                        border_width=1,
                                        border_color=("#e0e0e0", "#2a2a4a"))
        table_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)

        # Column headers
        header_frame = ctk.CTkFrame(table_container, fg_color=("#1a73e8", "#0d47a1"),
                                     corner_radius=0, height=40)
        header_frame.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))

        columns = ["#", "Timestamp", "Type", "X", "Y", "Width", "Height", "Area", "Confidence"]
        col_widths = [40, 160, 130, 60, 60, 60, 60, 70, 80]

        for i, (col, width) in enumerate(zip(columns, col_widths)):
            header_frame.grid_columnconfigure(i, weight=1 if i == 1 else 0, minsize=width)
            ctk.CTkLabel(
                header_frame, text=col,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white", width=width,
            ).grid(row=0, column=i, padx=5, pady=8)

        # Scrollable data area
        self.data_scroll = ctk.CTkScrollableFrame(
            table_container, fg_color="transparent",
        )
        self.data_scroll.grid(row=1, column=0, sticky="nsew", padx=1, pady=(0, 1))
        for i in range(len(columns)):
            self.data_scroll.grid_columnconfigure(i, weight=1 if i == 1 else 0,
                                                   minsize=col_widths[i])

        self._load_data()

    def _load_data(self):
        """Load data from change_log.csv."""
        # Clear existing
        for widget in self.data_scroll.winfo_children():
            widget.destroy()

        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "change_log.csv")
        if not os.path.exists(csv_path):
            ctk.CTkLabel(
                self.data_scroll, text="No detection history found.",
                font=ctk.CTkFont(size=13), text_color=("#aaa", "#666"),
            ).grid(row=0, column=0, columnspan=9, pady=30)
            return

        rows = []
        try:
            with open(csv_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 5:
                        # Try to detect rows with timestamp in first column
                        try:
                            datetime.strptime(row[0][:19], "%Y-%m-%d %H:%M:%S")
                            rows.append(row)
                        except (ValueError, IndexError):
                            pass
        except Exception:
            pass

        if not rows:
            ctk.CTkLabel(
                self.data_scroll, text="No valid records found in log.",
                font=ctk.CTkFont(size=13), text_color=("#aaa", "#666"),
            ).grid(row=0, column=0, columnspan=9, pady=30)
            return

        # Show last 200 rows (most recent first)
        rows = rows[-200:]
        rows.reverse()

        for idx, row in enumerate(rows):
            bg = ("#f8f9fa", "#1a1a35") if idx % 2 == 0 else ("#ffffff", "#1e1e3a")

            # Build display row
            display = [str(idx + 1)]
            display.append(row[0][:19] if len(row) > 0 else "—")
            display.append(row[1] if len(row) > 1 else "—")
            display.append(row[2] if len(row) > 2 else "—")
            display.append(row[3] if len(row) > 3 else "—")
            display.append(row[4] if len(row) > 4 else "—")
            display.append(row[5] if len(row) > 5 else "—")
            display.append(row[6] if len(row) > 6 else "—")
            display.append(row[7] if len(row) > 7 else "—")

            for col_idx, value in enumerate(display):
                # Color code the type column
                text_color = ("#333", "#ccc")
                if col_idx == 2:
                    type_colors = {
                        "Construction": ("#e65100", "#fb8c00"),
                        "Vegetation Change": ("#1b5e20", "#34a853"),
                        "Water Change": ("#0d47a1", "#4da6ff"),
                        "Demolition": ("#b71c1c", "#e53935"),
                    }
                    text_color = type_colors.get(value, text_color)

                lbl = ctk.CTkLabel(
                    self.data_scroll, text=str(value),
                    font=ctk.CTkFont(size=10),
                    text_color=text_color,
                    fg_color=bg,
                    corner_radius=0,
                )
                lbl.grid(row=idx, column=col_idx, padx=1, pady=1, sticky="ew")
