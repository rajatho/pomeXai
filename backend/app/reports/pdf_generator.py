"""PDF diagnosis report generation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_pdf_report(
    diagnosis: Dict[str, Any],
    image_path: Optional[str] = None,
    gradcam_path: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """Generate a downloadable PDF diagnosis report."""
    from app.config import get_settings

    settings = get_settings()
    out_dir = Path(output_dir or settings.resolved_reports_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"diagnosis_report_{uuid.uuid4().hex[:12]}.pdf"
    pdf_path = out_dir / filename

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Heading1"], fontSize=18, spaceAfter=12, textColor=colors.HexColor("#1B4332"))
    heading = styles["Heading2"]
    body = styles["BodyText"]
    elements = []

    elements.append(Paragraph("Pomegranate Disease Diagnosis Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body))
    elements.append(Spacer(1, 0.2 * inch))

    if image_path and Path(image_path).exists():
        try:
            elements.append(Paragraph("Uploaded Image", heading))
            elements.append(Image(image_path, width=3 * inch, height=3 * inch))
            elements.append(Spacer(1, 0.15 * inch))
        except Exception:
            pass

    elements.append(Paragraph("Prediction Summary", heading))
    summary_data = [
        ["Disease", diagnosis.get("disease_name", "N/A")],
        ["Confidence", f"{diagnosis.get('confidence', 0)}%"],
        ["Severity", diagnosis.get("severity", "N/A")],
        ["Affected Part", diagnosis.get("affected_part", "N/A")],
    ]
    table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Disease Description", heading))
    elements.append(Paragraph(diagnosis.get("description", ""), body))
    elements.append(Spacer(1, 0.15 * inch))

    rec = diagnosis.get("recommendations", {})
    elements.append(Paragraph("Fertilizer & Treatment Recommendations", heading))
    rec_rows = [
        ["Fertilizer", rec.get("fertilizer", "")],
        ["NPK Ratio", rec.get("npk_ratio", "")],
        ["Organic Fertilizer", rec.get("organic_fertilizer", "")],
        ["Bio Fertilizer", rec.get("bio_fertilizer", "")],
        ["Fungicide", rec.get("fungicide") or "Not required"],
        ["Pesticide", rec.get("pesticide") or "Not required"],
        ["Dosage", rec.get("dosage", "")],
        ["Spraying Interval", rec.get("spraying_interval", "")],
        ["Irrigation", rec.get("irrigation", "")],
        ["Recovery Time", rec.get("recovery_time", "")],
    ]
    rec_table = Table(rec_rows, colWidths=[2 * inch, 4 * inch])
    rec_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#FFF3E0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(rec_table)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Suggested Actions", heading))
    actions = rec.get("preventive_measures", []) + rec.get("organic_treatment", [])
    for action in actions:
        elements.append(Paragraph(f"• {action}", body))

    if gradcam_path and Path(gradcam_path).exists():
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph("Model Explainability (Grad-CAM)", heading))
        try:
            elements.append(Image(gradcam_path, width=5.5 * inch, height=2 * inch))
        except Exception:
            pass

    doc.build(elements)
    return str(pdf_path)
