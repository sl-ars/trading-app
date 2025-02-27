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

@shared_task(bind=True)
def generate_invoice(self, sales_order_id):
    """ Generate an invoice PDF asynchronously using ReportLab """

    try:
        sales_order = SalesOrder.objects.get(id=sales_order_id)

        # Create a new invoice or update existing one
        invoice, _ = Invoice.objects.get_or_create(sales_order=sales_order)

        # Generate PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = Paragraph("<b>INVOICE</b>", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Invoice Details
        invoice_details = [
            ["Invoice ID:", str(invoice.id)],
            ["Order ID:", str(sales_order.id)],
            ["Issued At:", str(invoice.issued_at)],
            ["Customer:", sales_order.order.user.username],
        ]

        table = Table(invoice_details, colWidths=[100, 300])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Product Details
        product_details = [
            ["Product", "Quantity", "Price", "Total"],
            [sales_order.order.product.title, str(sales_order.order.quantity),
             f"{sales_order.order.product.price} ₸", f"{sales_order.order.total_price} ₸"]
        ]

        product_table = Table(product_details, colWidths=[200, 100, 100, 100])
        product_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(product_table)
        elements.append(Spacer(1, 12))

        # Total Amount
        total_amount = Paragraph(f"<b>Total Amount:</b> {sales_order.order.total_price} ₸", styles["Normal"])
        elements.append(total_amount)
        elements.append(Spacer(1, 12))

        # Save PDF
        doc.build(elements)
        buffer.seek(0)

        # Save the PDF file to storage
        pdf_filename = f"invoice/order_{sales_order.id}.pdf"
        invoice.pdf_file.save(pdf_filename, ContentFile(buffer.read()), save=True)

        return f"Invoice generated for Order {sales_order.id}"

    except Exception as e:
        # Notify user about the failure
        notify_failure(sales_order.order.user, f"Failed to generate invoice for Order {sales_order.id}. Reason: {str(e)}")

        # Return failure reason
        self.update_state(state="FAILURE", meta={"error": str(e)})
        return f"Invoice generation failed: {str(e)}"

def notify_failure(user, message):
    """ Sends a WebSocket notification when invoice generation fails """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}", {"type": "notify", "message": message}
    )