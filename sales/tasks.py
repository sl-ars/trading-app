from celery import shared_task
from django.core.files.base import ContentFile
from reportlab.lib.units import inch

from sales.models import Invoice, SalesOrder
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.db import transaction, close_old_connections

import threading


@shared_task(bind=True)
def generate_invoice(self, sales_order_id):
    """ Generate an invoice PDF asynchronously using ReportLab """

    try:
        print("Step 1: Task Started")
        print(f"Sales Order ID: {sales_order_id}")

        # Ensure sales_order_id is an integer
        sales_order_id = int(sales_order_id)

        # Ensure old connections are closed properly
        close_old_connections()

        # Fetch Sales Order and related data inside a safe transaction block
        with transaction.atomic():
            sales_order = SalesOrder.objects.select_related(
                "order", "payment", "order__user", "order__product", "order__product__category"
            ).get(id=sales_order_id)
        print(f"Sales Order Fetched: {sales_order}")

        # Create or Fetch Existing Invoice
        invoice, created = Invoice.objects.get_or_create(sales_order=sales_order)

        # Prepare PDF Generation
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        styles = getSampleStyleSheet()
        elements = []

        # Header
        elements.append(Paragraph("<b>INVOICE</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Invoice and Order Details
        elements.append(Paragraph(f"Invoice ID: {invoice.id}", styles["Normal"]))
        elements.append(Paragraph(f"Order ID: {sales_order.order.id}", styles["Normal"]))
        elements.append(Paragraph(f"Order Status: {sales_order.status}", styles["Normal"]))
        elements.append(Paragraph(f"Total Price: {sales_order.total_price} KZT", styles["Normal"]))
        elements.append(Paragraph(f"Created At: {sales_order.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # User Information
        user = sales_order.order.user
        elements.append(Paragraph("<b>User Information</b>", styles["Heading2"]))
        elements.append(Paragraph(f"User Name: {user.username}", styles["Normal"]))
        elements.append(Paragraph(f"User Email: {user.email}", styles["Normal"]))
        elements.append(Paragraph(f"User Role: {user.get_role_display()}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Payment Information
        payment = sales_order.payment
        if payment:
            elements.append(Paragraph("<b>Payment Information</b>", styles["Heading2"]))
            elements.append(Paragraph(f"Payment Method: {payment.method}", styles["Normal"]))
            elements.append(Paragraph(f"Payment Status: {payment.status}", styles["Normal"]))
            elements.append(Paragraph(f"Payment Created At: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
            elements.append(Spacer(1, 12))

        # Product Information
        product = sales_order.order.product
        elements.append(Paragraph("<b>Product Information</b>", styles["Heading2"]))
        elements.append(Paragraph(f"Product Name: {product.title}", styles["Normal"]))
        elements.append(Paragraph(f"Product Description: {product.description}", styles["Normal"]))
        elements.append(Paragraph(f"Product Price: {product.price} KZT", styles["Normal"]))
        if product.category:
            elements.append(Paragraph(f"Product Category: {product.category.name}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Tabular Order Details
        elements.append(Paragraph("<b>Order Details</b>", styles["Heading2"]))

        order_data = [
            ["Item", "Quantity", "Unit Price", "Total Price"],
            [
                product.title,
                sales_order.order.quantity,
                f"{product.price} KZT",
                f"{sales_order.order.total_price} KZT",
            ],
        ]

        table = Table(order_data, colWidths=[2 * inch, inch, inch, inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

        # Use a threading lock for the PDF generation
        lock = threading.Lock()
        with lock:
            print("Starting PDF Generation")
            doc.build(elements)
            buffer.seek(0)
            print("PDF Generated Successfully")

        # Save the PDF to File Storage
        pdf_filename = f"invoice/order_{sales_order.id}.pdf"
        invoice.pdf_file.save(pdf_filename, ContentFile(buffer.read()), save=True)
        print(f"PDF Saved as {pdf_filename}")

        return f"Invoice generated for Order {sales_order.id}"

    except Exception as e:
        print(f"ERROR: Invoice generation failed: {str(e)}")
        self.update_state(state="FAILURE", meta={"error": str(e)})
        return f"Invoice generation failed: {str(e)}"