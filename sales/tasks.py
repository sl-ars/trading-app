from celery import shared_task
from django.core.files.base import ContentFile
from sales.models import Invoice, SalesOrder
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import connection
from django.db import transaction, close_old_connections


import threading

@shared_task(bind=True)
def generate_invoice(self, sales_order_id):
    """ Generate an invoice PDF asynchronously using ReportLab """

    try:
        print("Step 1: Task Started")
        print(f"Sales Order ID: {sales_order_id}")
        print(f"Sales Order ID Type: {type(sales_order_id)}")

        # Ensure sales_order_id is an integer
        try:
            sales_order_id = int(sales_order_id)
        except ValueError:
            raise Exception(f"Invalid Sales Order ID format: {sales_order_id}")

        # Ensure old connections are closed properly
        close_old_connections()

        # Fetch Sales Order inside a safe transaction block
        with transaction.atomic():
            sales_order = SalesOrder.objects.get(id=sales_order_id)
        print(f"Step 3: Sales Order Fetched: {sales_order}")

        # Create or Fetch Existing Invoice
        invoice, created = Invoice.objects.get_or_create(sales_order=sales_order)

        # Prepare PDF Generation
        buffer = BytesIO()
        print("Step 6: Buffer Created")

        doc = SimpleDocTemplate(buffer, pagesize=A4)
        print("Step 7: SimpleDocTemplate Created")

        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("<b>INVOICE</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Minimal PDF Content
        elements.append(Paragraph(f"Invoice ID: {invoice.id}", styles["Normal"]))
        elements.append(Paragraph(f"Order ID: {sales_order.id}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Use a threading lock for the PDF generation
        lock = threading.Lock()
        with lock:
            print("Step 8: Starting PDF Generation")
            doc.build(elements)
            buffer.seek(0)
            print("Step 9: PDF Generated Successfully")

        # Save the PDF to File Storage
        pdf_filename = f"invoice/order_{sales_order.id}.pdf"
        invoice.pdf_file.save(pdf_filename, ContentFile(buffer.read()), save=True)
        print(f"Step 10: PDF Saved as {pdf_filename}")

        return f"Invoice generated for Order {sales_order.id}"

    except Exception as e:
        print(f"ERROR: Invoice generation failed: {str(e)}")
        self.update_state(state="FAILURE", meta={"error": str(e)})
        return f"Invoice generation failed: {str(e)}"