from django.core.management.base import BaseCommand
from main.models import InputSet, Tryon, TryonBatch, Organization, Model, ModelVersion
import boto3
from tryon_menu.aws_constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME
)

class Command(BaseCommand):
    help = 'Nuke all application data except users and admin stuff'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input('This will delete ALL application data (images, batches, etc). Are you sure? [y/N]: ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION_NAME
        )

        try:
            # Delete all S3 objects
            self.stdout.write('Deleting S3 objects...')
            paginator = s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=AWS_STORAGE_BUCKET_NAME):
                if 'Contents' in page:
                    objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                    if objects_to_delete:
                        s3_client.delete_objects(
                            Bucket=AWS_STORAGE_BUCKET_NAME,
                            Delete={'Objects': objects_to_delete}
                        )
                        self.stdout.write(f'Deleted {len(objects_to_delete)} objects from S3')

            # Delete database records
            self.stdout.write('Deleting database records...')
            
            # Delete in correct order to respect foreign key constraints
            tryon_count = TryonBatch.objects.all().count()
            TryonBatch.objects.all().delete()
            self.stdout.write(f'Deleted {tryon_count} tryon batches')

            tryon_count = Tryon.objects.all().count()
            Tryon.objects.all().delete()
            self.stdout.write(f'Deleted {tryon_count} tryons')

            inputset_count = InputSet.objects.all().count()
            InputSet.objects.all().delete()
            self.stdout.write(f'Deleted {inputset_count} input sets')

            # modelversion_count = ModelVersion.objects.all().count()
            # ModelVersion.objects.all().delete()
            # self.stdout.write(f'Deleted {modelversion_count} model versions')

            # model_count = Model.objects.all().count()
            # Model.objects.all().delete()
            # self.stdout.write(f'Deleted {model_count} models')

            # org_count = Organization.objects.all().count()
            # Organization.objects.all().delete()
            # self.stdout.write(f'Deleted {org_count} organizations')

            self.stdout.write(self.style.SUCCESS('Successfully nuked all application data'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during nuke operation: {str(e)}')
            ) 