from django.core.management.base import BaseCommand
from main.models import InputSet
import boto3
from tryon_menu.aws_constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME
)

class Command(BaseCommand):
    help = 'Generate signed URLs for all S3 objects in InputSet model'

    def handle(self, *args, **options):
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION_NAME
        )

        # Maximum expiration time for presigned URLs (7 days in seconds)
        EXPIRATION = 7 * 24 * 60 * 60

        input_sets = InputSet.objects.all()
        for input_set in input_sets:
            try:
                # Extract S3 keys from URLs
                garment_key = input_set.garment_image.split(f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/")[1]
                model_key = input_set.model_image.split(f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/")[1]
                garment_thumb_key = input_set.garment_thumbnail_url.split(f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/")[1]
                model_thumb_key = input_set.model_thumbnail_url.split(f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/")[1]

                # Generate signed URLs
                garment_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': garment_key},
                    ExpiresIn=EXPIRATION
                )
                model_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': model_key},
                    ExpiresIn=EXPIRATION
                )
                garment_thumb_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': garment_thumb_key},
                    ExpiresIn=EXPIRATION
                )
                model_thumb_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': model_thumb_key},
                    ExpiresIn=EXPIRATION
                )

                # Update InputSet with signed URLs
                input_set.garment_image = garment_url
                input_set.model_image = model_url
                input_set.garment_thumbnail_url = garment_thumb_url
                input_set.model_thumbnail_url = model_thumb_url
                input_set.save()

                self.stdout.write(self.style.SUCCESS(f'Successfully updated signed URLs for InputSet {input_set.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating InputSet {input_set.id}: {str(e)}')) 