from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.graphics import renderPDF
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from svglib.svglib import svg2rlg, SvgRenderer

from lxml import etree


# DEFINE LAYOUT CONSTANTS
A4 = (210*mm,297*mm)
MARGIN_TOP = 20*mm
MARGIN_BOTTOM = 20*mm
MARGIN_LEFT = 15*mm
MARGIN_RIGHT = 15*mm
MAX_DRAWING_SIZE = 150
LINE_SPACE = 2
VERTICAL_SPACING = 15*mm
HORIZONTAL_SPACING = 15*mm

# Set the selected format. Other formats can be found in reportlab.lib.pagesizes
format = A4

class Invoice:

    def __init__(self):
        self.company_name = ""
        self.company_logo = ""
        self.company_VAT_number = ""
        self.company_registration_number = ""
        self.company_email = ""
        self.company_website = ""
        self.company_address = ""
        self.company_zip_city = ""
        self.company_phone = ""
        self.company_email = ""
        
        self.customer_number = ""
        self.customer_name = ""
        self.invoice_number = ""
        self.invoice_date = ""
        self.due_date = ""

        self.invoicing_address = ""
        self.invoicing_zip_city = ""
        self.invoicing_phone = ""
        self.invoicing_email = ""
        
        self.shipping_address = ""
        self.shipping_zip_city = ""
        self.shipping_phone = ""
        self.shipping_email = ""

        self.items = []
        self.VAT_rate = 0
        self.discount = 0
        self.payment_terms = []

    def generate_footer(self, c):
        c.resetTransforms()
        c.translate(MARGIN_LEFT, MARGIN_BOTTOM)
        c.setFillColorRGB(0.5,0.5,0.5)
        c.setFont("Helvetica",8)
        c.drawCentredString(0.5 * format[0] - MARGIN_LEFT, -0.5 * MARGIN_BOTTOM, f' {self.company_name} RCS {self.company_registration_number} - Numéro de TVA intracommunautaire {self.company_VAT_number}')

    def generate_header(self, c, current_page, total_pages):
        c.resetTransforms()
        c.setFillColorRGB(0.5,0.5,0.5)
        c.setFont("Helvetica",8)
        c.translate(MARGIN_LEFT, format[1] - 0.5 * MARGIN_TOP)
        c.drawString(0, 0, f"Page {current_page}/{total_pages}")
        c.drawRightString(format[0] - MARGIN_LEFT - MARGIN_RIGHT, 0 , f' {self.invoice_number}')

    def generate_details(self, c):
        c.translate(MARGIN_LEFT, format[1] - MARGIN_TOP)

        svg_root = etree.fromstring(self.company_logo)
        svgRenderer = SvgRenderer('')
        drawing = svgRenderer.render(svg_root)

        width = drawing.width
        height = drawing.height
        max_dimension = max(width, height)
        scale = MAX_DRAWING_SIZE/max_dimension
        if max_dimension > MAX_DRAWING_SIZE:
            drawing.scale(scale, scale)

        renderPDF.draw(
            drawing, 
            c, 
            0,
            - drawing.height * scale
        )
        c.translate(0, -drawing.height*scale)

        # Draw company details
        company_details_offset = c.stringWidth(f"{self.company_name}", "Helvetica-Bold", 18)
        for text in (f"{self.company_address}", f"{self.company_zip_city}", f"{self.company_phone}", f"{self.company_email}"):
            company_details_offset = max(company_details_offset, c.stringWidth(text, "Helvetica", 12))

        c.setFont("Helvetica-Bold", 18)
        c.translate(0, - VERTICAL_SPACING)
        c.drawString(0, 0, f"{self.company_name}")
        c.setFont("Helvetica", 12)
        c.translate(0, - 12 - LINE_SPACE)
        c.drawString(0, 0, f"{self.company_address}")
        c.translate(0, - 12 - LINE_SPACE)
        c.drawString(0, 0, f"{self.company_zip_city}")
        c.translate(0, - 12 - LINE_SPACE)
        c.drawString(0, 0, f"{self.company_phone}")
        c.translate(0, - 12 - LINE_SPACE)
        c.drawString(0, 0, f"{self.company_email}")
        c.translate(0, - 12 - LINE_SPACE)
        c.resetTransforms()

        customer_details_offset = c.stringWidth(f"Facture n°{self.invoice_number}", "Helvetica-Bold", 16)
        for text in (f"Numéro de client: {self.customer_number}",f"Date: {self.invoice_date}", f"Echéance: {self.due_date}", f"Client: {self.customer_name}"):
            customer_details_offset = max(customer_details_offset, c.stringWidth(text, "Helvetica", 12))

        c.translate(format[0] - MARGIN_RIGHT - customer_details_offset, format[1] -  MARGIN_TOP - 0.5 * VERTICAL_SPACING )
        c.setFont("Helvetica-Bold", 16)
        c.drawString(0, 0, f"Facture n°{self.invoice_number}")
        c.translate(0, - 16 - LINE_SPACE)
        c.setFont("Helvetica", 12)
        if (self.customer_number != ""):
            c.drawString(0, 0, f"Numéro de client: {self.customer_number}")
            c.translate(0, - 12 - LINE_SPACE)
        c.drawString(0, 0, f"Date: {self.invoice_date}")
        c.translate(0, - 12 - LINE_SPACE)
        c.drawString(0, 0, f"Echéance: {self.due_date}")
        c.translate(0, - 12 - LINE_SPACE)
        c.drawString(0, 0, f"Client: {self.customer_name}")

        invoice_details_offset = c.stringWidth(f"Addresse de", "Helvetica-Bold", 12)
        for text in (f"{self.invoicing_address}", f"{self.invoicing_zip_city}", f"{self.invoicing_phone}", f"{self.invoicing_email}"):
            invoice_details_offset = max(invoice_details_offset, c.stringWidth(text, "Helvetica", 10))

        c.translate(customer_details_offset - invoice_details_offset, - 12 - LINE_SPACE - 0.5 * VERTICAL_SPACING)
        c.saveState()
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0, 0, f"Adresse de")
        c.translate(0, - 12 - LINE_SPACE)
        c.drawString(0, 0, f"facturation")
        c.setFont("Helvetica", 10)
        c.translate(0, - 14 - LINE_SPACE)
        if (self.invoicing_address != ""):
            c.drawString(0, 0, f"{self.invoicing_address}")
            c.translate(0, - 10 - LINE_SPACE)
        if (self.invoicing_zip_city != ""):
            c.drawString(0, 0, f"{self.invoicing_zip_city}")
            c.translate(0, - 10 - LINE_SPACE)
        if (self.invoicing_phone != ""):
            c.drawString(0, 0, f"{self.invoicing_phone}")
            c.translate(0, - 10 - LINE_SPACE)
        c.drawString(0, 0, f"{self.invoicing_email}")

        if (self.shipping_address != "" or self.shipping_zip_city != "" or self.shipping_phone != "" or self.shipping_email != ""):
            c.restoreState()
            shipping_details_offset = c.stringWidth(f"Addresse de", "Helvetica-Bold", 12)
            for text in (f"{self.shipping_address}", f"{self.shipping_zip_city}", f"{self.shipping_phone}", f"{self.shipping_email}"):
                shipping_details_offset = max(shipping_details_offset, c.stringWidth(text, "Helvetica", 10))
            
            c.translate(- shipping_details_offset - HORIZONTAL_SPACING,0)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(0, 0, f"Adresse de")
            c.translate(0, - 12 - LINE_SPACE)
            c.drawString(0, 0, f"livraison")
            c.setFont("Helvetica", 10)
            c.translate(0, - 14 - LINE_SPACE)
            if (self.shipping_address != ""):
                c.drawString(0, 0, f"{self.shipping_address}")
                c.translate(0, - 10 - LINE_SPACE)
            if (self.shipping_zip_city != ""):
                c.drawString(0, 0, f"{self.shipping_zip_city}")
                c.translate(0, - 10 - LINE_SPACE)
            if (self.shipping_phone != ""):
                c.drawString(0, 0, f"{self.shipping_phone}")
                c.translate(0, - 10 - LINE_SPACE)
            c.drawString(0, 0, f"{self.shipping_email}")

            c.translate(shipping_details_offset + HORIZONTAL_SPACING + invoice_details_offset, - VERTICAL_SPACING)
            
        else :
            c.translate(invoice_details_offset, - VERTICAL_SPACING)
        c.translate(-format[0] + MARGIN_LEFT + MARGIN_RIGHT, 0)

    def generate_table(self,c, minimum_height=0):
        items_table_style = [
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.7,0.7,0.7)),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black), 
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]

        col_percentage = [0.55, 0.10, 0.20, 0.15]
        colWidth = [(format[0] - MARGIN_LEFT - MARGIN_RIGHT) * p for p in col_percentage]
        headers = ["Article", "Quantité", "Prix unitaire (€ HT)", "Total (€ HT)"]
        page_items = [[headers]]
        height_sum = 0
        for item in self.items[1:]:
            title_desc = Paragraph(f"<b>{item[0]}</b><br/>{item[1]}")
            height_sum += title_desc.wrap(colWidth[0],2147483647)[1]

            if (height_sum > 410 and len(page_items) == 1) or (len(page_items) > 1 and height_sum > 550):
                page_items.append([headers])
                height_sum = 0
            page_items[-1].append([title_desc, f"{item[2]}", f"{item[3]:.2f}", f"{item[2]*item[3]:.2f}"])

        add_last_page = 0
        if (height_sum > 440 - minimum_height and len(page_items) == 1) or (len(page_items) > 1 and height_sum > 640 - minimum_height):
            add_last_page = 1

        for i, page_item in enumerate(page_items):
            if i > 0:
                c.showPage()
                self.generate_header(c, i+1, len(page_items) + add_last_page)
                self.generate_footer(c)
                c.resetTransforms()
                c.translate(MARGIN_LEFT,format[1] - MARGIN_TOP)
            table = Table(page_item, colWidth)
            table.setStyle(TableStyle(items_table_style))
            table.wrapOn(c, 0, 0)
            table.drawOn(c, 0, -table._height)

            if (i == 0):
                self.generate_header(c, i+1, len(page_items) + add_last_page)
                self.generate_footer(c)

        if (add_last_page):
            c.showPage()
            self.generate_header(c, len(page_items) + 1, len(page_items) + add_last_page)
            self.generate_footer(c)
            c.resetTransforms()
            c.translate(MARGIN_LEFT, format[1] - MARGIN_TOP)
        else :
            c.translate(0, - table._height)

    def generate_pdf(self, name):
        c = canvas.Canvas(f"{name}.pdf", pagesize=A4)
        c.setTitle("Invoice")
        c.setAuthor(self.company_name)

        self.generate_details(c)

        total_table_style = [
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]
        col_percentage = [0.6, 0.4]
        total_table_colWidth = [(format[0] - MARGIN_LEFT - MARGIN_RIGHT) * 0.3 * p for p in col_percentage]
        total_table_data = [
            ["Total HT (€)", f"{sum(item[2]*item[3] for item in self.items[1:]):.2f}"],
            ["Taux de TVA", f"{self.VAT_rate:.2f}%"],
            ["Remise (€)", f"{self.discount:.2f}"],
            ["Total TTC (€)", f"{sum(item[2]*item[3] for item in self.items[1:]) * (1 + self.VAT_rate/100) - self.discount:.2f}"]
        ]

        total_table = Table(total_table_data, total_table_colWidth)
        total_table.setStyle(TableStyle(total_table_style))
        total_table.wrapOn(c, 0, 0)

        payment_terms_table_style = [
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.7,0.7,0.7)),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]
        payment_terms_items = [[Paragraph("<b>Remarques et conditions de paiement</b>")]]
        payment_terms_items.append([Paragraph("<br/>".join(self.payment_terms))])

        payment_terms_table_colWidth = [(format[0] - MARGIN_LEFT - MARGIN_RIGHT) * 0.5 ]
        payment_terms_table = Table(payment_terms_items, payment_terms_table_colWidth)
        payment_terms_table.setStyle(TableStyle(payment_terms_table_style))
        payment_terms_table.wrapOn(c, 0, 0)
        
        offset = max(payment_terms_table._height, total_table._height) + VERTICAL_SPACING
        self.generate_table(c, minimum_height=offset)

        # Draw recap tables
        payment_terms_table.drawOn(c, 0, -payment_terms_table._height)
        total_table.drawOn(c, format[0] - MARGIN_LEFT - MARGIN_RIGHT - total_table._width - 0.5 * HORIZONTAL_SPACING, - offset + VERTICAL_SPACING)

        self.generate_footer(c)
        c.save()

    def set_company_name(self, name):
        self.company_name = name
    def set_company_logo(self, image):
        self.company_logo = image
    def set_company_VAT_number(self, number):
        self.company_VAT_number = number
    def set_company_registration_number(self, number):
        self.company_registration_number = number
    def set_company_email(self, email):
        self.company_email = email
    def set_company_website(self, website):
        self.company_website = website
    def set_company_address(self, address):
        self.company_address = address
    def set_company_zip_city(self, zip_city):
        self.company_zip_city = zip_city
    def set_company_phone(self, phone):
        self.company_phone = phone
    def set_company_email(self, email):
        self.company_email = email
    

    def set_customer_number(self, number):
        self.customer_number = number
    def set_customer_name(self, name):
        self.customer_name = name
    def set_invoice_number(self, number):
        self.invoice_number = number
    def set_invoice_date(self, date):
        self.invoice_date = date
    def set_due_date(self, date):
        self.due_date = date

    def set_invoicing_address(self, address):
        self.invoicing_address = address
    def set_invoicing_zip_city(self, zip_city):
        self.invoicing_zip_city = zip_city
    def set_invoicing_phone(self, phone):
        self.invoicing_phone = phone
    def set_invoicing_email(self, email):
        self.invoicing_email = email

    def set_shipping_address(self, address):
        self.shipping_address = address
    def set_shipping_zip_city(self, zip_city):
        self.shipping_zip_city = zip_city
    def set_shipping_phone(self, phone):
        self.shipping_phone = phone
    def set_shipping_email(self, email):
        self.shipping_email = email
        
    def set_items(self, items):
        self.items = items
    def set_VAT_rate(self, rate):
        self.VAT_rate = rate
    def set_discount(self, discount):
        self.discount = discount
    def set_payment_terms(self, terms):
        self.payment_terms = terms