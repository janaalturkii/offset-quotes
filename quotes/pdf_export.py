from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .vat_utils import calculate_totals
NAVY = colors.HexColor("#002360")
from reportlab.platypus import Paragraph as PDFParagraph

def generate_quote_pdf(quote, line_items):
    """
    Build a branded Offset Events quote PDF and return it as bytes,
    ready to be served as an HTTP response.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'OffsetTitle', parent=styles['Title'], textColor=NAVY, fontSize=22
    )
    heading_style = ParagraphStyle(
        'OffsetHeading', parent=styles['Heading2'], textColor=NAVY
    )

    story = []

    story.append(Paragraph("OFFSET EVENTS", title_style))
    story.append(Paragraph("Brand Activation & Event Company — Jeddah", styles['Normal']))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"Quotation for: {quote.client_name or 'Client'}", heading_style))
    story.append(Paragraph(f"Date: {quote.created_at.strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Client Brief:", heading_style))
    story.append(Paragraph(quote.client_brief, styles['Normal']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Quotation Breakdown", heading_style))

    totals = calculate_totals(line_items)

    cell_style = ParagraphStyle('cell', parent=styles['Normal'], fontSize=9, leading=12)

    table_data = [["Description", "Category", "Price (SAR)"]]
    for item in line_items:
        table_data.append([
            PDFParagraph(item.description, cell_style),
            item.category,
            f"{item.estimated_price:,.2f}"
        ])

    table_data.append(["", "Subtotal", f"{totals['subtotal']:,.2f}"])
    if totals['vat_enabled']:
        table_data.append(["", f"VAT ({totals['vat_rate']}%)", f"{totals['vat_amount']:,.2f}"])
    table_data.append(["", "TOTAL", f"{totals['total']:,.2f} SAR"])

    table = Table(table_data, colWidths=[3.6 * inch, 1.4 * inch, 1.3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('LINEABOVE', (0, -1), (-1, -1), 1, NAVY),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor("#f4f4f4")]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
        
    story.append(table)
    story.append(Spacer(1, 20))

    vat_note = "This quotation includes VAT and is valid for 14 days." if totals['vat_enabled'] else "This quotation excludes VAT and is valid for 14 days."
    story.append(Paragraph(vat_note, styles['Italic']))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Contact: off.set.events1@gmail.com", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer