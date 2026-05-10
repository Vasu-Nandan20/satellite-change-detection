"""
settings_frame.py — Application settings and configuration panel.
"""

import customtkinter as ctk


class SettingsFrame(ctk.CTkFrame):
    """Application settings — appearance, defaults, and about info."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_settings()

    def _build_header(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0,
                               fg_color=("#f8f9fa", "#12122a"))
        header.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            header, text="⚙️  Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(padx=25, pady=15, anchor="w")

    def _build_settings(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        scroll.grid_columnconfigure(0, weight=1)

        # ── Appearance ──
        self._build_section(scroll, "🎨  Appearance", [
            self._appearance_widget,
            self._color_theme_widget,
            self._ui_scale_widget,
        ])

        # ── Default Detection Settings ──
        self._build_section(scroll, "🔍  Default Detection Settings", [
            self._default_alignment_widget,
            self._default_detection_widget,
            self._default_sensitivity_widget,
            self._default_min_area_widget,
        ])

        # ── About ──
        self._build_about_section(scroll)

    def _build_section(self, parent, title, widget_builders):
        section = ctk.CTkFrame(parent, corner_radius=12,
                                fg_color=("#ffffff", "#1e1e3a"),
                                border_width=1,
                                border_color=("#e0e0e0", "#2a2a4a"))
        section.pack(fill="x", pady=8)

        ctk.CTkLabel(
            section, text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1a73e8", "#4da6ff"),
        ).pack(padx=20, pady=(15, 10), anchor="w")

        for builder in widget_builders:
            builder(section)

    # ── Widget builders ──

    def _appearance_widget(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text="Appearance Mode",
                     font=ctk.CTkFont(size=12)).pack(side="left")

        mode_var = ctk.StringVar(value=ctk.get_appearance_mode())
        menu = ctk.CTkOptionMenu(
            f, variable=mode_var,
            values=["Dark", "Light", "System"],
            font=ctk.CTkFont(size=12), width=150,
            command=lambda v: ctk.set_appearance_mode(v),
        )
        menu.pack(side="right")

    def _color_theme_widget(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=(5, 15))
        ctk.CTkLabel(f, text="Color Theme",
                     font=ctk.CTkFont(size=12)).pack(side="left")

        theme_var = ctk.StringVar(value="blue")
        ctk.CTkOptionMenu(
            f, variable=theme_var,
            values=["blue", "green", "dark-blue"],
            font=ctk.CTkFont(size=12), width=150,
            command=lambda v: ctk.set_default_color_theme(v),
        ).pack(side="right")

    def _ui_scale_widget(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=(5, 15))
        ctk.CTkLabel(f, text="UI Scaling",
                     font=ctk.CTkFont(size=12)).pack(side="left")

        scale_var = ctk.StringVar(value="100%")
        ctk.CTkOptionMenu(
            f, variable=scale_var,
            values=["80%", "90%", "100%", "110%", "120%"],
            font=ctk.CTkFont(size=12), width=150,
            command=lambda v: ctk.set_widget_scaling(int(v.replace("%", "")) / 100),
        ).pack(side="right")

    def _default_alignment_widget(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text="Default Alignment",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        ctk.CTkOptionMenu(
            f, values=["ORB", "SIFT", "ECC"],
            font=ctk.CTkFont(size=12), width=150,
        ).pack(side="right")

    def _default_detection_widget(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text="Default Detection Method",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        ctk.CTkOptionMenu(
            f, values=["Absolute Difference", "SSIM", "Combined"],
            font=ctk.CTkFont(size=12), width=180,
        ).pack(side="right")

    def _default_sensitivity_widget(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text="Default Sensitivity",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        slider_f = ctk.CTkFrame(f, fg_color="transparent")
        slider_f.pack(side="right")
        ctk.CTkSlider(slider_f, from_=1, to=100, width=130).pack(side="left")
        ctk.CTkLabel(slider_f, text="50", font=ctk.CTkFont(size=11), width=30).pack(side="left")

    def _default_min_area_widget(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=(5, 15))
        ctk.CTkLabel(f, text="Default Min Area (px)",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        ctk.CTkEntry(f, placeholder_text="100",
                     font=ctk.CTkFont(size=12), width=150).pack(side="right")

    # ── About section ──

    def _build_about_section(self, parent):
        about = ctk.CTkFrame(parent, corner_radius=12,
                              fg_color=("#ffffff", "#1e1e3a"),
                              border_width=1,
                              border_color=("#e0e0e0", "#2a2a4a"))
        about.pack(fill="x", pady=8)

        ctk.CTkLabel(
            about, text="ℹ️  About SENTINEL",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1a73e8", "#4da6ff"),
        ).pack(padx=20, pady=(15, 5), anchor="w")

        info_lines = [
            "🛰️  SENTINEL — Satellite Change Detection System v2.0",
            "",
            "A professional-grade tool for detecting and analyzing",
            "changes in satellite imagery using advanced computer vision.",
            "",
            "Technologies Used:",
            "  • OpenCV (SIFT, ORB, ECC alignment)",
            "  • scikit-image (SSIM structural similarity)",
            "  • scikit-learn (KMeans classification)",
            "  • matplotlib (Interactive analytics)",
            "  • CustomTkinter (Modern dark UI)",
            "  • ReportLab (PDF report generation)",
            "",
            "© 2026 SENTINEL Project",
        ]

        for line in info_lines:
            ctk.CTkLabel(
                about, text=line,
                font=ctk.CTkFont(size=11),
                text_color=("#666", "#999"),
            ).pack(padx=25, anchor="w")

        ctk.CTkLabel(about, text="").pack(pady=5)
