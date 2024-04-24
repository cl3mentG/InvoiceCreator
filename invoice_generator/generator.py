from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.graphics import renderPDF
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from svglib.svglib import svg2rlg, SvgRenderer
import rapidjson
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
        """
        Initializes an instance of the InvoiceGenerator class.

        Attributes:
        - company_name: The name of the company.
        - company_logo: The logo of the company.
        - company_VAT_number: The VAT number of the company.
        - company_registration_number: The registration number of the company.
        - company_email: The email address of the company.
        - company_address: The address of the company.
        - company_zip_city: The ZIP code and city of the company.
        - company_phone: The phone number of the company.
        - customer_number: The customer number.
        - customer_name: The name of the customer.
        - invoice_number: The invoice number.
        - invoice_date: The date of the invoice.
        - due_date: The due date of the invoice.
        - invoicing_address: The invoicing address.
        - invoicing_zip_city: The ZIP code and city for invoicing.
        - invoicing_phone: The phone number for invoicing.
        - invoicing_email: The email address for invoicing.
        - shipping_address: The shipping address.
        - shipping_zip_city: The ZIP code and city for shipping.
        - shipping_phone: The phone number for shipping.
        - shipping_email: The email address for shipping.
        - items: The list of items in the invoice.
        - VAT_rate: The VAT rate for the invoice.
        - discount: The discount for the invoice.
        - payment_terms: The payment terms for the invoice.
        """
        self.company_name = ""
        self.company_logo = ""
        self.company_VAT_number = ""
        self.company_registration_number = ""
        self.company_email = ""
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

    def _generate_footer(self, c: canvas.Canvas):
        c.resetTransforms()
        c.translate(MARGIN_LEFT, MARGIN_BOTTOM)
        c.setFillColorRGB(0.5,0.5,0.5)
        c.setFont("Helvetica",8)
        c.drawCentredString(0.5 * format[0] - MARGIN_LEFT, -0.5 * MARGIN_BOTTOM, f' {self.company_name} RCS {self.company_registration_number} - Numéro de TVA intracommunautaire {self.company_VAT_number}')

    def _generate_header(self, c: canvas.Canvas, current_page: int, total_pages: int):
        c.resetTransforms()
        c.setFillColorRGB(0.5,0.5,0.5)
        c.setFont("Helvetica",8)
        c.translate(MARGIN_LEFT, format[1] - 0.5 * MARGIN_TOP)
        c.drawString(0, 0, f"Page {current_page}/{total_pages}")
        c.drawRightString(format[0] - MARGIN_LEFT - MARGIN_RIGHT, 0 , f' {self.invoice_number}')

    def _generate_details(self, c : canvas.Canvas):

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

    def _generate_table(self, c: canvas.Canvas, minimum_height = 0):
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
                self._generate_header(c, i+1, len(page_items) + add_last_page)
                self._generate_footer(c)
                c.resetTransforms()
                c.translate(MARGIN_LEFT,format[1] - MARGIN_TOP)
            table = Table(page_item, colWidth)
            table.setStyle(TableStyle(items_table_style))
            table.wrapOn(c, 0, 0)
            table.drawOn(c, 0, -table._height)

            if (i == 0):
                self._generate_header(c, i+1, len(page_items) + add_last_page)
                self._generate_footer(c)

        if (add_last_page):
            c.showPage()
            self._generate_header(c, len(page_items) + 1, len(page_items) + add_last_page)
            self._generate_footer(c)
            c.resetTransforms()
            c.translate(MARGIN_LEFT, format[1] - MARGIN_TOP)
        else :
            c.translate(0, - table._height)

    def generate_pdf(self, name : str):
        """
        Generates a PDF file with the invoice details.
        name : The name of the PDF file without the ".pdf" extension.
        """
        c = canvas.Canvas(f"{name}.pdf", pagesize=A4)
        c.setTitle(f"Facture_{self.invoice_number}")
        c.setAuthor(self.company_name)

        self._generate_details(c)

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
        self._generate_table(c, minimum_height=offset)

        # Draw recap tables
        payment_terms_table.drawOn(c, 0, -payment_terms_table._height)
        total_table.drawOn(c, format[0] - MARGIN_LEFT - MARGIN_RIGHT - total_table._width - 0.5 * HORIZONTAL_SPACING, - offset + VERTICAL_SPACING)

        self._generate_footer(c)
        c.save()


    def generate_from_json(json_str : str):
        """
        Generates an Invoice object from a JSON string.
        """
        data = rapidjson.loads(json_str)
        invoice = Invoice()
        try:
            invoice.company_name = data["company_name"]
            invoice.company_logo = data["company_logo"]
            invoice.company_VAT_number = data["company_VAT_number"]
            invoice.company_registration_number = data["company_registration_number"]
            invoice.company_email = data["company_email"]
            invoice.company_address = data["company_address"]
            invoice.company_zip_city = data["company_zip_city"]
            invoice.company_phone = data["company_phone"]
            invoice.company_email = data["company_email"]

            invoice.customer_number = data.get("customer_number", "")
            invoice.customer_name = data["customer_name"]
            invoice.invoice_number = data["invoice_number"]
            invoice.invoice_date = data["invoice_date"]
            invoice.due_date = data["due_date"]

            invoice.invoicing_address = data.get("invoicing_address", "")
            invoice.invoicing_zip_city = data.get("invoicing_zip_city", "")
            invoice.invoicing_phone = data.get("invoicing_phone", "")
            invoice.invoicing_email = data.get("invoicing_email", "")

            invoice.shipping_address = data.get("shipping_address", "")
            invoice.shipping_zip_city = data.get("shipping_zip_city", "")
            invoice.shipping_phone = data.get("shipping_phone", "")
            invoice.shipping_email = data.get("shipping_email", "")
            
            invoice.items = data["items"]
            invoice.VAT_rate = data["VAT_rate"]
            invoice.discount = data["discount"]
            invoice.payment_terms = data["payment_terms"]
        except KeyError:
            print("Error: JSON file does not contain all required fields.")
        return invoice
    