from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

NAVY = colors.HexColor("#002360")


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

    table_data = [["Description", "Category", "Price (SAR)"]]
    total = 0
    for item in line_items:
        table_data.append([item.description, item.category, f"{item.estimated_price:,.2f}"])
        total += float(item.estimated_price)

    table_data.append(["", "TOTAL", f"{total:,.2f} SAR"])

    table = Table(table_data, colWidths=[3.2 * inch, 1.5 * inch, 1.5 * inch])
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

    story.append(Paragraph("This quotation is VAT-inclusive and valid for 14 days.", styles['Italic']))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Contact: off.set.events1@gmail.com", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer