# Generated by Django 5.1.4 on 2024-12-26 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_remove_inputset_garment_image_old_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='model',
            name='url',
            field=models.URLField(blank=True, help_text="URL to the model's documentation or source", max_length=500),
        ),
    ]
