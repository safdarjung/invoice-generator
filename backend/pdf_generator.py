from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

def generate_invoice_table(form_data, styles):
    story = []
    table_header = ["SNo", "Description", "HSN CODE", "QTY", "Rate", "Amount"]
    table_data = [table_header]
    total_amount = 0
    for i, item in enumerate(form_data.get('items', [])):
        quantity_val = item.get('quantity', 0)
        rate_val = item.get('rate', 0)
        amount = (float(quantity_val or 0)) * (float(rate_val or 0))
        total_amount += amount
        table_data.append([
            str(i + 1),
            item.get('description', ''),
            item.get('hsn_code', '') or '',
            str(item.get('quantity', 0) or 0),
            f"{float(item.get('rate', 0) or 0):.2f}",
            f"{amount:.2f}"
        ])
    
    col_widths = [0.5*inch, 3*inch, 1*inch, 0.75*inch, 1*inch, 1.25*inch]
    item_table = Table(table_data, colWidths=col_widths)
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(item_table)
    story.append(Spacer(1, 0.25*inch))

    gst_percentage = float(form_data.get('gst_percentage', 0) or 0)
    gst_amount = (total_amount * gst_percentage) / 100
    transport_charge = float(form_data.get('transport_charge', 0) or 0)
    grand_total = total_amount + gst_amount + transport_charge
    advance = float(form_data.get('advance_payment', 0) or 0)
    balance = grand_total - advance

    totals_data = [
        ['Total', f"{total_amount:.2f}"],
        [f"GST ({(form_data.get('gst_percentage', 0) or 0)}%)", f"{gst_amount:.2f}"],
        ['Transport Charge', f"{transport_charge:.2f}"],
        ['Advance', f"{advance:.2f}"],
        ['Balance', f"{balance:.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[2*inch, 1.5*inch], hAlign='RIGHT')
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(totals_table)
    return story

def generate_quotation_paragraph(form_data, styles):
    story = []
    story.append(Paragraph("The prices for the items are as follows:", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    for item in form_data.get('items', []):
        item_text = f"- {item.get('description', '')} at Rs {float(item.get('rate', 0) or 0):.2f} per piece"
        story.append(Paragraph(item_text, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    return story

import uuid

def create_pdf(form_data, file_path=None):
    if file_path is None:
        file_path = f"/tmp/{uuid.uuid4()}.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    company_name_style = ParagraphStyle(
        'company_name',
        parent=styles['h1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    address_style = ParagraphStyle(
        'company_address',
        parent=styles['Normal'],
        alignment=TA_CENTER
    )

    story = []

    company_name = "M.S. ENTERPRISES"
    company_address = "5B-Sanjay Memorial Indl. Estate Phase-1, Near YMCA Chowk, N.I.T. FARIDABAD."
    company_contact = "TEL.NO-9811086746 | GSTIN:06AKQPM8903JIZN"

    story.append(Paragraph(company_name, company_name_style))
    story.append(Paragraph(company_address, address_style))
    story.append(Paragraph(company_contact, address_style))
    story.append(Spacer(1, 0.25*inch))

    story.append(Paragraph(f"<b>To:</b> {form_data.get('client_name', '')}", styles['Normal']))
    story.append(Paragraph(form_data.get('client_address', ''), styles['Normal']))
    story.append(Paragraph(f"<b>GSTIN:</b> {form_data.get('client_gstin', '')}", styles['Normal']))
    story.append(Spacer(1, 0.25*inch))

    is_invoice = bool(form_data.get('invoice_number') and form_data.get('invoice_date'))

    if is_invoice:
        story.append(Paragraph(f"<b>PERFORMA INVOICE NO:</b> {form_data.get('invoice_number', '')}", styles['h3']))
        story.append(Paragraph(f"<b>Date:</b> {form_data.get('invoice_date', '')}", styles['h3']))
        story.append(Spacer(1, 0.25*inch))
        story.extend(generate_invoice_table(form_data, styles))
    else:
        story.append(Paragraph("<b>QUOTATION</b>", styles['h3']))
        story.append(Spacer(1, 0.25*inch))
        story.extend(generate_quotation_paragraph(form_data, styles))

    if not is_invoice:
        if form_data.get('minimum_quantity'):
            story.append(Paragraph(f"<b>Minimum Quantity:</b> {form_data.get('minimum_quantity', '')}", styles['Normal']))
        if form_data.get('delivery_time'):
            story.append(Paragraph(f"<b>Delivery time:</b> {form_data.get('delivery_time', '')}", styles['Normal']))
        if form_data.get('payment_terms'):
            story.append(Paragraph(f"<b>Payment:</b> {form_data.get('payment_terms', '')}", styles['Normal']))
        story.append(Paragraph("Transportation Charges extra", styles['Normal']))
        story.append(Paragraph("If Sample is required from our end, that will be charged extra", styles['Normal']))
        story.append(Paragraph("Packing Charges Extra", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

    story.append(Paragraph("<b>Thanks and Regards</b>", styles['Normal']))
    story.append(Paragraph("Nasir Khan", styles['Normal']))
    story.append(Paragraph("+91 9811086746", styles['Normal']))
    story.append(Spacer(1, 0.25*inch))
    
    bank_details = [
        Paragraph("<b>Our Bank Details:</b>", styles['Normal']),
        Paragraph("PUNJAB NATIONAL BANK, A/C", styles['Normal']),
        Paragraph("No. 0483050019340", styles['Normal']),
        Paragraph("IFSC- PUNB0048320", styles['Normal']),
    ]
    
    footer_table = Table([[bank_details]], colWidths=[7.5*inch])
    story.append(footer_table)

    doc.build(story)
    return file_path