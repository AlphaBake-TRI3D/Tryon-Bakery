# Generated by Django 5.1.4 on 2024-12-30 17:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_inputset_mode_inputset_prompt_tryon_mode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='model',
            name='organization',
        ),
        migrations.DeleteModel(
            name='Organization',
        ),
    ]
