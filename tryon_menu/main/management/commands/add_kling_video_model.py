from django.core.management.base import BaseCommand
from main.models import Organization, Model, ModelVersion

class Command(BaseCommand):
    help = 'Add KlingVideo model to the database'

    def handle(self, *args, **kwargs):
        # Get or create the organization
        org, created = Organization.objects.get_or_create(
            name='KlingAI',
            defaults={'description': 'Better natural garment folds'}
        )
        if created:
            self.stdout.write(f'Created organization: {org.name}')

        # Create KlingVideo model
        kling_video_model, created = Model.objects.get_or_create(
            name='Kling Video Model',
            organization=org,
            defaults={
                'description': 'Kling video generation model',
                'model_type': 'video'
            }
        )
        if created:
            self.stdout.write(f'Created Kling video model: {kling_video_model.name}')

        # Create KlingVideo model version
        kling_video_model_version, created = ModelVersion.objects.get_or_create(
            model=kling_video_model,
            version='1.0',
            defaults={
                'resolution': 1080,
                'description': 'Initial version of Kling video model',
                'elo_rating': 1500,
                'is_api_implemented': True,
                'tray_code': 'kling_video_v1',
                'price_per_inference': 0.05,
                'model_type': 'video'
            }
        )
        if created:
            self.stdout.write(f'Created Kling video model version: {kling_video_model_version.version}') 