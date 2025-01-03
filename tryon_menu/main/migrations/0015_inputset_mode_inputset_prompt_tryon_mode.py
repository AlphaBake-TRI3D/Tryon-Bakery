# Generated by Django 5.1.4 on 2024-12-30 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_model_model_type_modelversion_model_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputset',
            name='mode',
            field=models.CharField(choices=[('image', 'Image'), ('video', 'Video')], default='image', max_length=10),
        ),
        migrations.AddField(
            model_name='inputset',
            name='prompt',
            field=models.TextField(blank=True, help_text='Prompt for video generation'),
        ),
        migrations.AddField(
            model_name='tryon',
            name='mode',
            field=models.CharField(choices=[('image', 'Image'), ('video', 'Video')], default='image', max_length=10),
        ),
    ]
