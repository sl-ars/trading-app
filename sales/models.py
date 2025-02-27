from django.db import models
from django.conf import settings
from .storage import InvoiceStorage
from trading.models import Order
from django.utils.timezone import now
from django.core.files.storage import default_storage
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="sales_order")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def update_status_from_stripe(self, payment_status):
        """ Updates SalesOrder and Order status based on Stripe payment status """
        if payment_status == "succeeded":
            self.status = "paid"
            self.order.status = "paid"
        elif payment_status in ["failed", "canceled"]:
            self.status = "failed"
            self.order.status = "failed"

        self.order.save()
        self.save()

    def __str__(self):
        return f"Sales Order {self.id} for Order {self.order.id} - {self.status}"


class Invoice(models.Model):
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, related_name="invoice")
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(storage=InvoiceStorage(), upload_to="pdf/", blank=True, null=True)

    def __str__(self):
        return f"Invoice for Order {self.sales_order.id}"


    def delete(self, *args, **kwargs):
        """ Deletes the associated PDF file from storage when the invoice is deleted """

        if self.pdf_file and self.pdf_file.name:
            default_storage.delete(self.pdf_file.name)
        super().delete(*args, **kwargs)

    def get_download_url(self):
        """ Generates a signed S3 URL using AWS4-HMAC-SHA256 for secure invoice download """

        if self.pdf_file and self.pdf_file.name:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            s3_key = self.pdf_file.name
            if not s3_key.startswith("invoice/"):
                s3_key = f"invoice/{s3_key}"

            try:
                signed_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                        "Key": s3_key
                    },
                    ExpiresIn=600,
                    HttpMethod="GET",
                )

                # signed_url += "&response-content-disposition=inline"

                return signed_url

            except NoCredentialsError:

                return None
            except ClientError as e:

                return None

        return None

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('stripe', 'Stripe')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, related_name="payment", null=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='stripe')
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def update_status(self, stripe_status):
        """ Updates payment status based on Stripe webhook & updates SalesOrder/Order """
        self.status = stripe_status
        self.save()

        if self.sales_order:
            self.sales_order.update_status_from_stripe(stripe_status)

    def __str__(self):
        return f"Payment for Sales Order {self.sales_order.id} - {self.status}"