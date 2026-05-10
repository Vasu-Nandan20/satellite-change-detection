"""
analytics_frame.py — Interactive charts and visualizations using matplotlib.
"""

import customtkinter as ctk
import numpy as np

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class AnalyticsFrame(ctk.CTkFrame):
    """Analytics dashboard with embedded matplotlib charts."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        self.results = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_charts_area()

    def _build_header(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0,
                               fg_color=("#f8f9fa", "#12122a"))
        header.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            header, text="📊  Analytics & Visualizations",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(padx=25, pady=15, anchor="w")

    def _build_charts_area(self):
        self.charts_frame = ctk.CTkFrame(self, corner_radius=12,
                                          fg_color=("#ffffff", "#1e1e3a"),
                                          border_width=1,
                                          border_color=("#e0e0e0", "#2a2a4a"))
        self.charts_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))

        self.placeholder = ctk.CTkLabel(
            self.charts_frame,
            text="📊  Run a detection first to see analytics here.\n\n"
                 "Charts will include:\n"
                 "• Change area distribution histogram\n"
                 "• Change type pie chart\n"
                 "• Change density heatmap grid\n"
                 "• Confidence distribution",
            font=ctk.CTkFont(size=14),
            text_color=("#aaa", "#666"),
            justify="center",
        )
        self.placeholder.pack(expand=True)

        self.canvas_widget = None

    def update_data(self, results):
        """Called from detection frame when new results are available."""
        self.results = results
        self._render_charts()

    def _render_charts(self):
        if not HAS_MATPLOTLIB or not self.results:
            return

        # Clear previous
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
        self.placeholder.pack_forget()

        summary = self.results["summary"]
        classifications = self.results["classifications"]
        analyzer = self.results["analyzer"]

        # Determine colors based on appearance mode
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = "#1e1e3a" if is_dark else "#ffffff"
        text_color = "#cccccc" if is_dark else "#333333"
        grid_color = "#333355" if is_dark else "#e0e0e0"

        fig = Figure(figsize=(12, 8), dpi=100, facecolor=bg_color)

        # ── Chart 1: Area Distribution ──
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_facecolor(bg_color)
        if classifications:
            areas = [c["area"] for c in classifications]
            ax1.hist(areas, bins=min(20, len(areas)), color="#1a73e8",
                     edgecolor="#0d47a1", alpha=0.85)
        ax1.set_title("Change Area Distribution", color=text_color, fontsize=11, fontweight="bold")
        ax1.set_xlabel("Area (pixels)", color=text_color, fontsize=9)
        ax1.set_ylabel("Count", color=text_color, fontsize=9)
        ax1.tick_params(colors=text_color, labelsize=8)
        ax1.grid(True, alpha=0.3, color=grid_color)

        # ── Chart 2: Type Breakdown Pie ──
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.set_facecolor(bg_color)
        type_data = summary.get("type_breakdown", {})
        if type_data:
            labels = list(type_data.keys())
            sizes = list(type_data.values())
            pie_colors = ["#1a73e8", "#34a853", "#fb8c00", "#e53935", "#7c4dff"]
            wedges, texts, autotexts = ax2.pie(
                sizes, labels=labels, autopct="%1.0f%%",
                colors=pie_colors[:len(labels)],
                textprops={"color": text_color, "fontsize": 9},
                startangle=90,
            )
            for at in autotexts:
                at.set_fontsize(8)
                at.set_color("white")
        ax2.set_title("Change Type Breakdown", color=text_color, fontsize=11, fontweight="bold")

        # ── Chart 3: Density Grid ──
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.set_facecolor(bg_color)
        density = analyzer.compute_grid_density(8, 8)
        im = ax3.imshow(density, cmap="YlOrRd", interpolation="nearest", aspect="auto")
        ax3.set_title("Change Density Grid", color=text_color, fontsize=11, fontweight="bold")
        ax3.tick_params(colors=text_color, labelsize=8)
        cbar = fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(colors=text_color, labelsize=8)

        # ── Chart 4: Confidence Distribution ──
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.set_facecolor(bg_color)
        if classifications:
            confidences = [c["confidence"] for c in classifications]
            ax4.hist(confidences, bins=min(15, len(confidences)),
                     color="#34a853", edgecolor="#1b5e20", alpha=0.85)
        ax4.set_title("Confidence Distribution", color=text_color, fontsize=11, fontweight="bold")
        ax4.set_xlabel("Confidence", color=text_color, fontsize=9)
        ax4.set_ylabel("Count", color=text_color, fontsize=9)
        ax4.tick_params(colors=text_color, labelsize=8)
        ax4.grid(True, alpha=0.3, color=grid_color)

        fig.tight_layout(pad=3.0)

        # Embed in tkinter
        self.canvas_widget = FigureCanvasTkAgg(fig, self.charts_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
