"""Lightweight PDF generation helpers built on ReportLab."""
import io
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable,
)


def clinic_header_flowables(styles):
    """Build a branded clinic header (logo + name/address/contact) from settings."""
    try:
        from apps.dashboard.models import ClinicInfo

        clinic = ClinicInfo.load()
    except Exception:
        clinic = None

    story = []
    name_style = ParagraphStyle("ClinicName", parent=styles["Title"], fontSize=18, spaceAfter=2)
    meta_style = ParagraphStyle("ClinicMeta", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#475569"))

    if clinic and getattr(clinic, "logo", None) and clinic.logo:
        try:
            path = clinic.logo.path
            if os.path.exists(path):
                story.append(Image(path, width=120, height=48, kind="proportional"))
        except Exception:
            pass

    name = clinic.name if clinic else "Dental Clinic"
    story.append(Paragraph(name, name_style))
    if clinic:
        parts = [p for p in [clinic.address, clinic.phone, clinic.email] if p]
        if parts:
            story.append(Paragraph(" · ".join(parts), meta_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d9488")))
    story.append(Spacer(1, 8))
    return story


def _doc(buffer):
    return SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )


def build_pdf(title, intro_lines, table_header=None, table_rows=None, footer=None):
    """Render a simple titled document with an optional table. Returns bytes."""
    buffer = io.BytesIO()
    doc = _doc(buffer)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 8)]

    for line in intro_lines or []:
        story.append(Paragraph(line, styles["Normal"]))
    story.append(Spacer(1, 10))

    if table_header and table_rows is not None:
        data = [table_header] + table_rows
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d9488")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#f1f5f9")]),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        story.append(table)

    if footer:
        story.append(Spacer(1, 16))
        story.append(Paragraph(footer, styles["Italic"]))

    doc.build(story)
    return buffer.getvalue()


def build_branded_pdf(title, intro_lines, table_header=None, table_rows=None,
                      footer=None, signature=None, signature_image=None):
    """Like build_pdf but with a clinic-branded header and optional signature block."""
    buffer = io.BytesIO()
    doc = _doc(buffer)
    styles = getSampleStyleSheet()
    story = clinic_header_flowables(styles)

    story.append(Paragraph(title, ParagraphStyle("DocTitle", parent=styles["Heading2"],
                                                  textColor=colors.HexColor("#0f766e"))))
    story.append(Spacer(1, 6))

    for line in intro_lines or []:
        story.append(Paragraph(line, styles["Normal"]))
    story.append(Spacer(1, 10))

    if table_header and table_rows is not None:
        data = [table_header] + table_rows
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d9488")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#f1f5f9")]),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        story.append(table)

    if footer:
        story.append(Spacer(1, 14))
        story.append(Paragraph(footer, ParagraphStyle("Footer", parent=styles["Normal"],
                                                       fontSize=8, textColor=colors.HexColor("#64748b"))))

    if signature or signature_image:
        story.append(Spacer(1, 40))
        if signature_image and os.path.exists(signature_image):
            try:
                story.append(Image(signature_image, width=120, height=40, kind="proportional", hAlign="RIGHT"))
            except Exception:
                pass
        sig_style = ParagraphStyle("Sig", parent=styles["Normal"], alignment=2)  # right
        story.append(HRFlowable(width="35%", thickness=0.5, color=colors.grey, hAlign="RIGHT"))
        story.append(Paragraph(signature or "", sig_style))

    doc.build(story)
    return buffer.getvalue()
