"""
detection_frame.py — Core detection workflow UI.

Step-by-step interface: load images → configure → run detection → view results.
"""

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import os
import cv2
import numpy as np

from engine.alignment import ImageAligner
from engine.detector import ChangeDetector
from engine.classifier import ChangeClassifier
from engine.analyzer import ChangeAnalyzer
from utils.image_utils import cv2_to_pil, load_image, resize_to_match
from utils.report_generator import export_csv, export_pdf


class DetectionFrame(ctk.CTkFrame):
    """Main detection workflow frame."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app

        # State
        self.img1_path = None
        self.img2_path = None
        self.img_before = None
        self.img_after = None
        self.results = None  # Stores last analysis results

        # Thumbnail references (prevent garbage collection)
        self._thumb1 = None
        self._thumb2 = None
        self._result_photo = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_bar()
        self._build_main_content()

    # ================================================================== #
    #  Top bar with title                                                  #
    # ================================================================== #

    def _build_top_bar(self):
        top = ctk.CTkFrame(self, height=60, corner_radius=0,
                           fg_color=("#f8f9fa", "#12122a"))
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            top, text="🔍  Change Detection",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=25, pady=15, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(top, height=4, corner_radius=2,
                                                progress_color="#1a73e8")
        self.progress_bar.grid(row=0, column=1, padx=20, sticky="ew")
        self.progress_bar.set(0)

    # ================================================================== #
    #  Main content — left config, right results                           #
    # ================================================================== #

    def _build_main_content(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=5)
        main.grid_rowconfigure(0, weight=1)

        self._build_config_panel(main)
        self._build_results_panel(main)

    # ------------------------------------------------------------------ #
    #  Left: Configuration Panel                                           #
    # ------------------------------------------------------------------ #

    def _build_config_panel(self, parent):
        config = ctk.CTkScrollableFrame(parent, corner_radius=12,
                                         fg_color=("#ffffff", "#1e1e3a"),
                                         border_width=1,
                                         border_color=("#e0e0e0", "#2a2a4a"),
                                         width=320)
        config.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=5)

        # ── STEP 1: Load Images ──
        ctk.CTkLabel(config, text="STEP 1 — Load Images",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=("#1a73e8", "#4da6ff")).pack(padx=15, pady=(15, 10), anchor="w")

        # Before image
        img1_frame = ctk.CTkFrame(config, fg_color="transparent")
        img1_frame.pack(padx=15, fill="x")

        ctk.CTkButton(
            img1_frame, text="📂  Select Before Image",
            font=ctk.CTkFont(size=12), height=36, corner_radius=8,
            fg_color=("#e8f0fe", "#1a2744"),
            text_color=("#1a73e8", "#4da6ff"),
            hover_color=("#d0e0fc", "#233a5c"),
            command=self._select_image1,
        ).pack(fill="x", pady=(0, 5))

        self.thumb1_label = ctk.CTkLabel(img1_frame, text="No image selected",
                                          font=ctk.CTkFont(size=10),
                                          text_color=("#999", "#666"))
        self.thumb1_label.pack(pady=(0, 8))

        # After image
        img2_frame = ctk.CTkFrame(config, fg_color="transparent")
        img2_frame.pack(padx=15, fill="x")

        ctk.CTkButton(
            img2_frame, text="📂  Select After Image",
            font=ctk.CTkFont(size=12), height=36, corner_radius=8,
            fg_color=("#e8f0fe", "#1a2744"),
            text_color=("#1a73e8", "#4da6ff"),
            hover_color=("#d0e0fc", "#233a5c"),
            command=self._select_image2,
        ).pack(fill="x", pady=(0, 5))

        self.thumb2_label = ctk.CTkLabel(img2_frame, text="No image selected",
                                          font=ctk.CTkFont(size=10),
                                          text_color=("#999", "#666"))
        self.thumb2_label.pack(pady=(0, 8))

        # Divider
        ctk.CTkFrame(config, height=1, fg_color=("#e0e0e0", "#333")).pack(fill="x", padx=15, pady=10)

        # ── STEP 2: Configuration ──
        ctk.CTkLabel(config, text="STEP 2 — Configuration",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=("#1a73e8", "#4da6ff")).pack(padx=15, pady=(5, 10), anchor="w")

        # Alignment method
        ctk.CTkLabel(config, text="Alignment Method",
                     font=ctk.CTkFont(size=11),
                     text_color=("#666", "#999")).pack(padx=15, anchor="w")

        self.align_var = ctk.StringVar(value="ORB")
        ctk.CTkOptionMenu(
            config, variable=self.align_var,
            values=["ORB", "SIFT", "ECC"],
            font=ctk.CTkFont(size=12),
            height=32, corner_radius=8,
            fg_color=("#e8f0fe", "#1a2744"),
            button_color=("#1a73e8", "#1a73e8"),
        ).pack(padx=15, fill="x", pady=(2, 8))

        # Detection method
        ctk.CTkLabel(config, text="Detection Method",
                     font=ctk.CTkFont(size=11),
                     text_color=("#666", "#999")).pack(padx=15, anchor="w")

        self.detect_var = ctk.StringVar(value="Absolute Difference")
        ctk.CTkOptionMenu(
            config, variable=self.detect_var,
            values=["Absolute Difference", "SSIM", "Combined"],
            font=ctk.CTkFont(size=12),
            height=32, corner_radius=8,
            fg_color=("#e8f0fe", "#1a2744"),
            button_color=("#1a73e8", "#1a73e8"),
        ).pack(padx=15, fill="x", pady=(2, 8))

        # Sensitivity slider
        ctk.CTkLabel(config, text="Sensitivity",
                     font=ctk.CTkFont(size=11),
                     text_color=("#666", "#999")).pack(padx=15, anchor="w")

        sens_frame = ctk.CTkFrame(config, fg_color="transparent")
        sens_frame.pack(padx=15, fill="x", pady=(2, 8))

        self.sensitivity_var = ctk.IntVar(value=50)
        self.sens_slider = ctk.CTkSlider(
            sens_frame, from_=1, to=100,
            variable=self.sensitivity_var,
            progress_color="#1a73e8",
            command=self._on_sens_change,
        )
        self.sens_slider.pack(side="left", expand=True, fill="x")

        self.sens_label = ctk.CTkLabel(sens_frame, text="50",
                                        font=ctk.CTkFont(size=11, weight="bold"),
                                        width=30)
        self.sens_label.pack(side="right", padx=5)

        # Min area
        ctk.CTkLabel(config, text="Min Contour Area (px)",
                     font=ctk.CTkFont(size=11),
                     text_color=("#666", "#999")).pack(padx=15, anchor="w")

        self.min_area_var = ctk.StringVar(value="100")
        ctk.CTkEntry(
            config, textvariable=self.min_area_var,
            font=ctk.CTkFont(size=12),
            height=32, corner_radius=8,
        ).pack(padx=15, fill="x", pady=(2, 12))

        # Divider
        ctk.CTkFrame(config, height=1, fg_color=("#e0e0e0", "#333")).pack(fill="x", padx=15, pady=5)

        # ── STEP 3: Run ──
        ctk.CTkLabel(config, text="STEP 3 — Run Detection",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=("#1a73e8", "#4da6ff")).pack(padx=15, pady=(10, 10), anchor="w")

        self.run_btn = ctk.CTkButton(
            config, text="🚀  Run Detection",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=48, corner_radius=10,
            fg_color=("#34a853", "#2e7d32"),
            hover_color=("#2e7d32", "#1b5e20"),
            command=self._run_detection,
        )
        self.run_btn.pack(padx=15, fill="x", pady=(0, 8))

        self.status_text = ctk.CTkLabel(config, text="",
                                         font=ctk.CTkFont(size=11),
                                         text_color=("#888", "#888"))
        self.status_text.pack(padx=15, anchor="w")

        # ── Export buttons ──
        ctk.CTkFrame(config, height=1, fg_color=("#e0e0e0", "#333")).pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(config, text="Export Results",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=("#1a73e8", "#4da6ff")).pack(padx=15, pady=(5, 8), anchor="w")

        export_frame = ctk.CTkFrame(config, fg_color="transparent")
        export_frame.pack(padx=15, fill="x", pady=(0, 15))
        export_frame.grid_columnconfigure(0, weight=1)
        export_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            export_frame, text="📄 PDF",
            font=ctk.CTkFont(size=12), height=34, corner_radius=8,
            fg_color=("#e53935", "#c62828"),
            hover_color=("#c62828", "#b71c1c"),
            command=self._export_pdf,
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

        ctk.CTkButton(
            export_frame, text="📊 CSV",
            font=ctk.CTkFont(size=12), height=34, corner_radius=8,
            fg_color=("#fb8c00", "#e65100"),
            hover_color=("#e65100", "#bf360c"),
            command=self._export_csv,
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        ctk.CTkButton(
            config, text="💾  Save Result Image",
            font=ctk.CTkFont(size=12), height=34, corner_radius=8,
            fg_color=("#7c4dff", "#6200ea"),
            hover_color=("#6200ea", "#4a148c"),
            command=self._save_image,
        ).pack(padx=15, fill="x", pady=(0, 20))

    # ------------------------------------------------------------------ #
    #  Right: Results Panel                                                #
    # ------------------------------------------------------------------ #

    def _build_results_panel(self, parent):
        results = ctk.CTkFrame(parent, corner_radius=12,
                               fg_color=("#ffffff", "#1e1e3a"),
                               border_width=1,
                               border_color=("#e0e0e0", "#2a2a4a"))
        results.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=5)
        results.grid_columnconfigure(0, weight=1)
        results.grid_rowconfigure(1, weight=1)

        # View mode tabs
        tabs_frame = ctk.CTkFrame(results, fg_color="transparent")
        tabs_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))

        self.view_mode = ctk.StringVar(value="annotated")
        modes = [
            ("Annotated", "annotated"),
            ("Heatmap", "heatmap"),
            ("Before", "before"),
            ("After", "after"),
            ("Mask", "mask"),
            ("Side-by-Side", "sidebyside"),
        ]
        for i, (label, mode) in enumerate(modes):
            ctk.CTkButton(
                tabs_frame, text=label,
                font=ctk.CTkFont(size=11),
                height=30, width=85, corner_radius=6,
                fg_color=("#e8f0fe", "#1a2744"),
                text_color=("#1a73e8", "#4da6ff"),
                hover_color=("#d0e0fc", "#233a5c"),
                command=lambda m=mode: self._switch_view(m),
            ).pack(side="left", padx=2)

        # Image display area
        self.result_display = ctk.CTkLabel(
            results, text="Results will appear here after detection.\n\nLoad images and click 'Run Detection' to begin.",
            font=ctk.CTkFont(size=14),
            text_color=("#aaa", "#666"),
        )
        self.result_display.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)

        # Stats bar at bottom
        self.stats_bar = ctk.CTkFrame(results, height=50, corner_radius=0,
                                       fg_color=("#f0f4f8", "#151530"))
        self.stats_bar.grid(row=2, column=0, sticky="ew", padx=0, pady=0)

        self.stats_labels = {}
        stat_names = ["Changes", "Changed %", "Avg Confidence", "Method"]
        for i, name in enumerate(stat_names):
            self.stats_bar.grid_columnconfigure(i, weight=1)
            f = ctk.CTkFrame(self.stats_bar, fg_color="transparent")
            f.grid(row=0, column=i, padx=10, pady=8)
            ctk.CTkLabel(f, text=name, font=ctk.CTkFont(size=10),
                         text_color=("#999", "#666")).pack()
            lbl = ctk.CTkLabel(f, text="—", font=ctk.CTkFont(size=13, weight="bold"))
            lbl.pack()
            self.stats_labels[name] = lbl

    # ================================================================== #
    #  Event Handlers                                                      #
    # ================================================================== #

    def _on_sens_change(self, value):
        self.sens_label.configure(text=str(int(value)))

    def _select_image1(self):
        path = filedialog.askopenfilename(
            title="Select Before Image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
        )
        if path:
            self.img1_path = path
            self.img_before = load_image(path)
            # Show thumbnail
            thumb = cv2_to_pil(self.img_before)
            thumb.thumbnail((280, 120))
            self._thumb1 = ctk.CTkImage(light_image=thumb, dark_image=thumb,
                                         size=thumb.size)
            self.thumb1_label.configure(image=self._thumb1, text="")

    def _select_image2(self):
        path = filedialog.askopenfilename(
            title="Select After Image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
        )
        if path:
            self.img2_path = path
            self.img_after = load_image(path)
            thumb = cv2_to_pil(self.img_after)
            thumb.thumbnail((280, 120))
            self._thumb2 = ctk.CTkImage(light_image=thumb, dark_image=thumb,
                                         size=thumb.size)
            self.thumb2_label.configure(image=self._thumb2, text="")

    def _run_detection(self):
        if self.img_before is None or self.img_after is None:
            self.status_text.configure(text="⚠️  Please select both images first.",
                                        text_color="#e53935")
            return

        self.run_btn.configure(state="disabled", text="⏳ Processing...")
        self.status_text.configure(text="Running detection pipeline...",
                                    text_color=("#1a73e8", "#4da6ff"))
        self.progress_bar.set(0.1)

        # Run in background thread
        thread = threading.Thread(target=self._detection_worker, daemon=True)
        thread.start()

    def _detection_worker(self):
        try:
            before = self.img_before
            after = self.img_after

            # Step 1: Resize to match
            self._update_progress(0.15, "Resizing images...")
            after = resize_to_match(after, before.shape)

            # Step 2: Alignment
            self._update_progress(0.25, f"Aligning images ({self.align_var.get()})...")
            aligner = ImageAligner(method=self.align_var.get())
            aligned, align_score = aligner.align(before, after)

            # Step 3: Detection
            self._update_progress(0.50, f"Detecting changes ({self.detect_var.get()})...")
            min_area = int(self.min_area_var.get()) if self.min_area_var.get().isdigit() else 100
            detector = ChangeDetector(
                method=self.detect_var.get(),
                sensitivity=self.sensitivity_var.get(),
                min_area=min_area,
            )
            contours, mask, raw_diff = detector.detect(before, aligned)

            # Step 4: Classification
            self._update_progress(0.70, "Classifying changes...")
            classifier = ChangeClassifier()
            classifications = classifier.classify_contours(contours, before, aligned)

            # Step 5: Analysis
            self._update_progress(0.85, "Computing analytics...")
            analyzer = ChangeAnalyzer(before.shape, contours, classifications, mask, raw_diff)
            summary = analyzer.compute_summary()
            heatmap = analyzer.generate_heatmap(aligned)
            annotated = analyzer.generate_annotated_image(aligned)

            # Store results
            self.results = {
                "before": before,
                "after": aligned,
                "annotated": annotated,
                "heatmap": heatmap,
                "mask": mask,
                "raw_diff": raw_diff,
                "contours": contours,
                "classifications": classifications,
                "summary": summary,
                "analyzer": analyzer,
                "align_score": align_score,
            }

            # Log to CSV
            self._log_to_csv(classifications, summary)

            # Update UI on main thread
            self._update_progress(1.0, "Done!")
            self.after(100, self._display_results)

        except Exception as e:
            self.after(0, lambda: self.status_text.configure(
                text=f"❌ Error: {str(e)}", text_color="#e53935"))
            self.after(0, lambda: self.run_btn.configure(
                state="normal", text="🚀  Run Detection"))

    def _update_progress(self, value, text):
        self.after(0, lambda: self.progress_bar.set(value))
        self.after(0, lambda: self.status_text.configure(text=f"⏳ {text}"))

    def _display_results(self):
        """Update the UI with detection results."""
        if not self.results:
            return

        self.run_btn.configure(state="normal", text="🚀  Run Detection")
        summary = self.results["summary"]

        # Update stats bar
        self.stats_labels["Changes"].configure(
            text=str(summary["total_changes"]),
            text_color="#e53935" if summary["total_changes"] > 0 else "#34a853")
        self.stats_labels["Changed %"].configure(
            text=f"{summary['change_percentage']:.1f}%")
        self.stats_labels["Avg Confidence"].configure(
            text=f"{summary['avg_confidence']:.0%}")
        self.stats_labels["Method"].configure(
            text=self.detect_var.get()[:10])

        self.status_text.configure(
            text=f"✅ Detection complete — {summary['total_changes']} changes found.",
            text_color="#34a853")

        # Show annotated view by default
        self._switch_view("annotated")

        # Notify analytics frame
        if self.app and hasattr(self.app, 'frames') and 'analytics' in self.app.frames:
            self.app.frames['analytics'].update_data(self.results)

    def _switch_view(self, mode):
        """Switch the displayed result image."""
        if not self.results:
            return

        self.view_mode.set(mode)

        if mode == "annotated":
            img = self.results["annotated"]
        elif mode == "heatmap":
            img = self.results["heatmap"]
        elif mode == "before":
            img = self.results["before"]
        elif mode == "after":
            img = self.results["after"]
        elif mode == "mask":
            mask = self.results["mask"]
            img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        elif mode == "sidebyside":
            from utils.image_utils import create_side_by_side
            img = create_side_by_side(self.results["before"], self.results["annotated"])
        else:
            return

        # Display image
        pil = cv2_to_pil(img)
        # Get display area size
        display_w = self.result_display.winfo_width()
        display_h = self.result_display.winfo_height()
        if display_w < 100:
            display_w = 800
        if display_h < 100:
            display_h = 550
        pil.thumbnail((display_w - 20, display_h - 20), Image.Resampling.LANCZOS)

        self._result_photo = ctk.CTkImage(light_image=pil, dark_image=pil,
                                           size=pil.size)
        self.result_display.configure(image=self._result_photo, text="")

    # ------------------------------------------------------------------ #
    #  Export Functions                                                     #
    # ------------------------------------------------------------------ #

    def _export_pdf(self):
        if not self.results:
            self.status_text.configure(text="⚠️  Run detection first.", text_color="#e53935")
            return

        path = filedialog.asksaveasfilename(
            title="Save PDF Report",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile="sentinel_report.pdf",
        )
        if path:
            try:
                export_pdf(
                    self.results["classifications"],
                    self.results["summary"],
                    {
                        "before": self.results["before"],
                        "after": self.results["after"],
                        "annotated": self.results["annotated"],
                        "heatmap": self.results["heatmap"],
                    },
                    path,
                )
                self.status_text.configure(text=f"✅ PDF saved: {os.path.basename(path)}",
                                            text_color="#34a853")
            except Exception as e:
                self.status_text.configure(text=f"❌ PDF error: {e}", text_color="#e53935")

    def _export_csv(self):
        if not self.results:
            self.status_text.configure(text="⚠️  Run detection first.", text_color="#e53935")
            return

        path = filedialog.asksaveasfilename(
            title="Save CSV Report",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="sentinel_report.csv",
        )
        if path:
            try:
                export_csv(self.results["classifications"], self.results["summary"], path)
                self.status_text.configure(text=f"✅ CSV saved: {os.path.basename(path)}",
                                            text_color="#34a853")
            except Exception as e:
                self.status_text.configure(text=f"❌ CSV error: {e}", text_color="#e53935")

    def _save_image(self):
        if not self.results:
            self.status_text.configure(text="⚠️  Run detection first.", text_color="#e53935")
            return

        path = filedialog.asksaveasfilename(
            title="Save Result Image",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")],
            initialfile="detected_changes.png",
        )
        if path:
            try:
                mode = self.view_mode.get()
                if mode == "heatmap":
                    img = self.results["heatmap"]
                else:
                    img = self.results["annotated"]
                cv2.imwrite(path, img)
                self.status_text.configure(text=f"✅ Image saved: {os.path.basename(path)}",
                                            text_color="#34a853")
            except Exception as e:
                self.status_text.configure(text=f"❌ Save error: {e}", text_color="#e53935")

    # ------------------------------------------------------------------ #
    #  CSV Logging                                                         #
    # ------------------------------------------------------------------ #

    def _log_to_csv(self, classifications, summary):
        import csv
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "change_log.csv")
        file_exists = os.path.isfile(csv_path)
        try:
            with open(csv_path, mode="a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Timestamp", "Type", "X", "Y", "Width", "Height", "Area", "Confidence"])
                for cls in classifications:
                    x, y, w, h = cls["bbox"]
                    writer.writerow([
                        summary["timestamp"], cls["type"],
                        x, y, w, h, cls["area"], cls["confidence"]
                    ])
        except Exception:
            pass
