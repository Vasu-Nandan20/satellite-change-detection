"""
report_generator.py — PDF and CSV report generation for analysis results.
"""

import csv
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage,
        PageBreak,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

import cv2
import numpy as np
from utils.image_utils import cv2_to_pil


def export_csv(classifications, summary, filepath):
    """Export detection results to a CSV file."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header info
        writer.writerow(["SENTINEL — Satellite Change Detection Report"])
        writer.writerow(["Generated", summary.get("timestamp", "")])
        writer.writerow([])

        # Summary section
        writer.writerow(["=== SUMMARY ==="])
        writer.writerow(["Total Changes", summary.get("total_changes", 0)])
        writer.writerow(["Changed Pixels", summary.get("changed_pixels", 0)])
        writer.writerow(["Total Pixels", summary.get("total_pixels", 0)])
        writer.writerow(["Change %", f"{summary.get('change_percentage', 0):.2f}%"])
        writer.writerow(["Avg Confidence", f"{summary.get('avg_confidence', 0):.2f}"])
        writer.writerow([])

        # Type breakdown
        writer.writerow(["=== TYPE BREAKDOWN ==="])
        for t, count in summary.get("type_breakdown", {}).items():
            writer.writerow([t, count])
        writer.writerow([])

        # Detail rows
        writer.writerow(["=== CHANGE DETAILS ==="])
        writer.writerow(["#", "Type", "X", "Y", "Width", "Height", "Area", "Confidence"])
        for i, cls in enumerate(classifications, 1):
            x, y, w, h = cls["bbox"]
            writer.writerow([
                i, cls["type"], x, y, w, h,
                cls["area"], f"{cls['confidence']:.2f}"
            ])

    return filepath


def export_pdf(classifications, summary, images, filepath):
    """Generate a professional PDF report.

    Parameters
    ----------
    images : dict with keys 'before', 'after', 'annotated', 'heatmap' (all BGR np arrays)
    """
    if not HAS_REPORTLAB:
        raise ImportError("reportlab is required for PDF generation")

    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=22, spaceAfter=12, textColor=colors.HexColor("#1a73e8"),
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle", parent=styles["Heading2"],
        fontSize=14, spaceAfter=8, textColor=colors.HexColor("#333333"),
    )
    body_style = styles["Normal"]

    elements = []

    # ─── Title ────
    elements.append(Paragraph("🛰️ SENTINEL", title_style))
    elements.append(Paragraph("Satellite Change Detection Report", subtitle_style))
    elements.append(Paragraph(
        f"Generated: {summary.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}",
        body_style,
    ))
    elements.append(Spacer(1, 20))

    # ─── Summary Table ────
    elements.append(Paragraph("Analysis Summary", subtitle_style))
    summary_data = [
        ["Metric", "Value"],
        ["Total Changes Detected", str(summary.get("total_changes", 0))],
        ["Change Percentage", f"{summary.get('change_percentage', 0):.2f}%"],
        ["Changed Pixels", f"{summary.get('changed_pixels', 0):,}"],
        ["Average Change Area", f"{summary.get('avg_change_area', 0):.0f} px"],
        ["Largest Change Area", f"{summary.get('max_change_area', 0):,} px"],
        ["Average Confidence", f"{summary.get('avg_confidence', 0):.0%}"],
    ]
    t = Table(summary_data, colWidths=[3 * inch, 3 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # ─── Type Breakdown ────
    type_data = summary.get("type_breakdown", {})
    if type_data:
        elements.append(Paragraph("Change Type Breakdown", subtitle_style))
        bd = [["Type", "Count"]]
        for tp, cnt in type_data.items():
            bd.append([tp, str(cnt)])
        t2 = Table(bd, colWidths=[3 * inch, 3 * inch])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34a853")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0fff0"), colors.white]),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 20))

    # ─── Images ────
    for key, label in [("before", "Before Image"), ("after", "After Image"),
                       ("annotated", "Detected Changes"), ("heatmap", "Change Heatmap")]:
        if key in images and images[key] is not None:
            elements.append(Paragraph(label, subtitle_style))
            # Save temp image
            temp_path = os.path.join(os.path.dirname(filepath), f"_temp_{key}.png")
            pil = cv2_to_pil(images[key])
            pil.save(temp_path)
            img_w, img_h = pil.size
            max_w = 6 * inch
            scale = max_w / img_w
            elements.append(RLImage(temp_path, width=max_w, height=img_h * scale))
            elements.append(Spacer(1, 15))

    # ─── Detail Table ────
    if classifications:
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Change Log", subtitle_style))
        detail_data = [["#", "Type", "X", "Y", "W", "H", "Area", "Conf."]]
        for i, cls in enumerate(classifications[:50], 1):  # Cap at 50
            x, y, w, h = cls["bbox"]
            detail_data.append([
                str(i), cls["type"], str(x), str(y), str(w), str(h),
                str(cls["area"]), f"{cls['confidence']:.0%}"
            ])
        t3 = Table(detail_data, colWidths=[0.4*inch, 1.3*inch, 0.6*inch, 0.6*inch,
                                            0.6*inch, 0.6*inch, 0.8*inch, 0.6*inch])
        t3.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(t3)

    doc.build(elements)

    # Clean up temp images
    for key in ["before", "after", "annotated", "heatmap"]:
        temp_path = os.path.join(os.path.dirname(filepath), f"_temp_{key}.png")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

    return filepath
