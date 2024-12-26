from django.db import models
from django.utils import timezone

class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Model(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

class ModelVersion(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=50)
    resolution = models.IntegerField(help_text="Resolution in pixels")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.model.name} v{self.version}"

    class Meta:
        ordering = ['-created_at']

class InputSet(models.Model):
    name = models.CharField(max_length=200)
    garment_image = models.CharField(max_length=500, help_text="Path to garment image")
    model_image = models.CharField(max_length=500, help_text="Path to model image")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Tryon(models.Model):
    input_set = models.ForeignKey(InputSet, on_delete=models.CASCADE, related_name='tryons')
    model_version = models.ForeignKey(ModelVersion, on_delete=models.CASCADE, related_name='tryons')
    image_path = models.CharField(max_length=500)
    notes = models.JSONField(default=dict, help_text="Store positive and negative notes as JSON")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.model_version} - {self.input_set.name}"

class TryonBatch(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tryons = models.ManyToManyField(Tryon, related_name='batches')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tryon Batches"
