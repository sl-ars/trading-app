from storages.backends.s3boto3 import S3Boto3Storage

class ProductStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False