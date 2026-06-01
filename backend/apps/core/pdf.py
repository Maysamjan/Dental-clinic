"""Lightweight PDF generation helpers built on ReportLab."""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)


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
