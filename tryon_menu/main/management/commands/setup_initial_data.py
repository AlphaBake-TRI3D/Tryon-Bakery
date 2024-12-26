import os
import json
from django.core.management.base import BaseCommand
from main.models import Organization, Model, ModelVersion, InputSet, Tryon, TryonBatch
from django.conf import settings

class Command(BaseCommand):
    help = 'Setup initial data for the tryon comparison system'

    def handle(self, *args, **kwargs):
        # Create organizations
        orgs_data = [
            {'name': 'FashnAI', 'description': 'Great with finer text prints and replication'},
            {'name': 'KlingAI', 'description': 'Better natural garment folds'},
            {'name': 'OpenFlux', 'description': 'Open source solution'},
        ]
        
        orgs = {}
        for org_data in orgs_data:
            org, created = Organization.objects.get_or_create(
                name=org_data['name'],
                defaults={'description': org_data['description']}
            )
            orgs[org.name] = org
            if created:
                self.stdout.write(f'Created organization: {org.name}')

        # Create models and versions
        models_data = {
            'FashnAI': {'resolution': 768},
            'KlingAI': {'resolution': 1024},
            'OpenFlux': {'resolution': 1024},
        }

        model_versions = {}
        for org_name, model_data in models_data.items():
            model, created = Model.objects.get_or_create(
                name=f'{org_name} Tryon',
                organization=orgs[org_name],
                defaults={'description': f'Virtual try-on model by {org_name}'}
            )
            if created:
                self.stdout.write(f'Created model: {model.name}')

            version, created = ModelVersion.objects.get_or_create(
                model=model,
                version='1.0',
                defaults={
                    'resolution': model_data['resolution'],
                    'description': f'Initial version of {org_name} try-on model'
                }
            )
            model_versions[org_name] = version
            if created:
                self.stdout.write(f'Created model version: {version}')

        # Create input set
        input_set, created = InputSet.objects.get_or_create(
            name='Basic Example',
            defaults={
                'garment_image': 'inputs/garments/GfPWMBQXIAAFRZ1.jpeg',
                'model_image': 'inputs/models/00008_00.jpg'
            }
        )
        if created:
            self.stdout.write(f'Created input set: {input_set.name}')

        # Create tryons
        tryon_data = {
            'FashnAI': {
                'notes': {
                    'positive': ['Great with finer text prints and replication'],
                    'negative': ['Resolution: 768', 'Flat folds compared to KlingAI']
                }
            },
            'KlingAI': {
                'notes': {
                    'positive': ['More natural garment folds', 'Resolution: 1024'],
                    'negative': ['Blurry garment details']
                }
            },
            'OpenFlux': {
                'notes': {
                    'positive': ['Resolution: 1024'],
                    'negative': ['Missed the cuffs design, blurrier than FashnAI', 'Flat folds compared to KlingAI']
                }
            }
        }

        tryons = []
        for org_name, data in tryon_data.items():
            tryon, created = Tryon.objects.get_or_create(
                input_set=input_set,
                model_version=model_versions[org_name],
                defaults={
                    'image_path': f'outputs/tryons/{org_name}.png',
                    'notes': data['notes']
                }
            )
            tryons.append(tryon)
            if created:
                self.stdout.write(f'Created tryon: {tryon}')

        # Create tryon batch
        batch, created = TryonBatch.objects.get_or_create(
            name='Initial Comparison',
            defaults={
                'description': 'Comparison of FashnAI, KlingAI, and OpenFlux models'
            }
        )
        if created:
            self.stdout.write(f'Created tryon batch: {batch.name}')
        
        batch.tryons.set(tryons)
        self.stdout.write(self.style.SUCCESS('Successfully set up initial data')) 