from django.core.management.base import BaseCommand
from main.models import Organization, Model, ModelVersion
from django.utils import timezone

class Command(BaseCommand):
    help = 'Sets up initial model data including organizations, models, and model versions'

    def handle(self, *args, **kwargs):
        # Create Organizations
        orgs_data = [
            {
                'name': 'FASHNAI',
                'description': 'Leading virtual try-on solution with high-quality image generation'
            },
            {
                'name': 'KLINGAI',
                'description': 'Advanced AI-powered virtual try-on platform'
            },
            {
                'name': 'VModelAI',
                'description': 'Innovative virtual try-on technology provider'
            },
            {
                'name': 'REPLICATE',
                'description': 'Platform for running AI models in the cloud'
            },
        ]

        self.stdout.write('Creating Organizations...')
        orgs = {}
        for org_data in orgs_data:
            org, created = Organization.objects.get_or_create(
                name=org_data['name'],
                defaults={
                    'description': org_data['description']
                }
            )
            orgs[org.name] = org
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"  {status}: Organization {org.name}")

        # Create Models
        models_data = [
            {
                'name': 'FASHNAI TRYON IMAGE',
                'organization': orgs['FASHNAI'],
                'description': 'High-fidelity virtual try-on model by FASHNAI',
                'url': 'https://fashn.ai/'
            },
            {
                'name': 'KLINGAI TRYON IMAGE',
                'organization': orgs['KLINGAI'],
                'description': 'Advanced virtual try-on model by KLINGAI',
                'url': 'https://kling.ai/'
            },
            {
                'name': 'VModelAI TRYON IMAGE',
                'organization': orgs['VModelAI'],
                'description': 'State-of-the-art virtual try-on model by VModelAI',
                'url': 'https://www.vmodel.ai/'
            },
            {
                'name': 'IDM-VTON-CUUUPID',
                'organization': orgs['REPLICATE'],
                'description': 'Open-source virtual try-on model available on Replicate',
                'url': 'https://replicate.com/'
            },
        ]

        self.stdout.write('\nCreating Models...')
        models = {}
        for model_data in models_data:
            model, created = Model.objects.get_or_create(
                name=model_data['name'],
                defaults={
                    'organization': model_data['organization'],
                    'description': model_data['description'],
                    'url': model_data['url']
                }
            )
            models[model.name] = model
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"  {status}: Model {model.name}")

        # Create Model Versions
        versions_data = [
            {
                'model': models['FASHNAI TRYON IMAGE'],
                'version': '20241229',
                'resolution': 1600,  # Using 1600 for "1.6 TRYON IMAGE"
                'description': 'Latest production version with improved image quality',
                'is_api_implemented': True,
                'tray_code': 'fashnai',
                'elo_rating': 1500,  # Starting ELO rating
            },
            {
                'model': models['KLINGAI TRYON IMAGE'],
                'version': '20241229',
                'resolution': 1600,
                'description': 'Latest version with enhanced garment draping',
                'is_api_implemented': True,
                'tray_code': 'klingai',
                'elo_rating': 1500,
            },
            {
                'model': models['VModelAI TRYON IMAGE'],
                'version': '20241229',
                'resolution': 1600,
                'description': 'Production version with advanced pose handling',
                'is_api_implemented': False,  # Only VModelAI has no API implementation
                'tray_code': '',  # Empty tray_code since no API
                'elo_rating': 1500,
            },
            {
                'model': models['IDM-VTON-CUUUPID'],
                'version': 'c871bb9b',
                'resolution': 1600,
                'description': 'Latest stable version on Replicate',
                'is_api_implemented': True,
                'tray_code': 'replicate',
                'elo_rating': 1500,
            },
        ]

        self.stdout.write('\nCreating/Updating Model Versions...')
        for version_data in versions_data:
            version, created = ModelVersion.objects.update_or_create(
                model=version_data['model'],
                version=version_data['version'],
                defaults={
                    'resolution': version_data['resolution'],
                    'description': version_data['description'],
                    'is_api_implemented': version_data['is_api_implemented'],
                    'tray_code': version_data['tray_code'],
                    'elo_rating': version_data['elo_rating'],
                    'created_at': timezone.now(),
                }
            )
            status = 'Created' if created else 'Updated'
            api_status = "API Ready" if version.is_api_implemented else "Manual Upload"
            self.stdout.write(f"  {status}: ModelVersion {version.model.name} v{version.version} ({api_status})")

        self.stdout.write(self.style.SUCCESS('\nSuccessfully set up and updated model data')) 