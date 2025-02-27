from storages.backends.s3boto3 import S3Boto3Storage

class InvoiceStorage(S3Boto3Storage):
    location = "invoice"
    file_overwrite = False