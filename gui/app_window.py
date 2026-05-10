"""
app_window.py — Main application window with sidebar navigation.

Professional dark-themed CustomTkinter window with animated sidebar
and multi-frame content area.
"""

import customtkinter as ctk


class AppWindow(ctk.CTk):
    """Main application window for SENTINEL."""

    def __init__(self):
        super().__init__()

        # ── Window config ──
        self.title("🛰️ SENTINEL — Satellite Change Detection System")
        self.geometry("1400x900")
        self.minsize(1200, 750)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Grid layout ──
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        self._build_sidebar()

        # ── Content area ──
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # ── Frame registry ──
        self.frames = {}
        self.current_frame = None

    def _build_sidebar(self):
        """Build the left navigation sidebar."""
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0,
                               fg_color=("#e8eaed", "#1a1a2e"))
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)

        # Logo / Brand
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=15, pady=(20, 5), sticky="ew")

        ctk.CTkLabel(
            brand_frame, text="🛰️ SENTINEL",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1a73e8", "#4da6ff"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_frame, text="Change Detection v2.0",
            font=ctk.CTkFont(size=11),
            text_color=("#666", "#888"),
        ).pack(anchor="w", pady=(0, 5))

        # Divider
        ctk.CTkFrame(sidebar, height=2,
                     fg_color=("#ccc", "#333")).grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        # Nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("🏠  Dashboard",   "dashboard",  2),
            ("🔍  Detection",   "detection",  3),
            ("📊  Analytics",   "analytics",  4),
            ("📋  History",     "history",     5),
            ("⚙️  Settings",    "settings",    6),
        ]

        for text, name, row in nav_items:
            btn = ctk.CTkButton(
                sidebar, text=text, anchor="w",
                font=ctk.CTkFont(size=14),
                height=42, corner_radius=8,
                fg_color="transparent",
                text_color=("#333", "#ccc"),
                hover_color=("#d0d7de", "#2a2a4a"),
                command=lambda n=name: self.show_frame(n),
            )
            btn.grid(row=row, column=0, padx=10, pady=3, sticky="ew")
            self.nav_buttons[name] = btn

        # Status bar at bottom
        status_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        status_frame.grid(row=11, column=0, padx=15, pady=(5, 15), sticky="sew")

        self.status_label = ctk.CTkLabel(
            status_frame, text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=("#888", "#666"),
        )
        self.status_label.pack(anchor="w")

        self.status_indicator = ctk.CTkLabel(
            status_frame, text="● Online",
            font=ctk.CTkFont(size=10),
            text_color=("#34a853", "#4ade80"),
        )
        self.status_indicator.pack(anchor="w")

    def register_frame(self, name, frame_class, **kwargs):
        """Register a content frame by name."""
        frame = frame_class(self.content_frame, **kwargs)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames[name] = frame
        frame.grid_remove()  # Hide initially

    def show_frame(self, name):
        """Switch to the named frame."""
        if self.current_frame and self.current_frame in self.frames:
            self.frames[self.current_frame].grid_remove()

        # Update button styles
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(
                    fg_color=("#1a73e8", "#1a73e8"),
                    text_color="white",
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("#333", "#ccc"),
                )

        if name in self.frames:
            self.frames[name].grid()
            self.current_frame = name

    def set_status(self, text, color=None):
        """Update the sidebar status label."""
        self.status_label.configure(text=text)
        if color:
            self.status_indicator.configure(text_color=color)
