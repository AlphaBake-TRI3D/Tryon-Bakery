# Generated by Django 5.1.4 on 2024-12-26 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_inputset_garment_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inputset',
            name='garment_image_old',
        ),
        migrations.RemoveField(
            model_name='inputset',
            name='garment_thumbnail_url_old',
        ),
        migrations.RemoveField(
            model_name='inputset',
            name='model_image_old',
        ),
        migrations.RemoveField(
            model_name='inputset',
            name='model_thumbnail_url_old',
        ),
        migrations.RemoveField(
            model_name='tryon',
            name='image_path',
        ),
        migrations.RemoveField(
            model_name='tryon',
            name='thumbnail_url',
        ),
        migrations.AddField(
            model_name='tryon',
            name='image_key',
            field=models.CharField(blank=True, help_text='S3 key for tryon image', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='tryon',
            name='thumb_key',
            field=models.CharField(blank=True, help_text='S3 key for tryon thumbnail', max_length=500, null=True),
        ),
    ]
