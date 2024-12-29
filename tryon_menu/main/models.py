from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import boto3
from tryon_menu.aws_constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME
)

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
    url = models.URLField(max_length=500, blank=True, help_text="URL to the model's documentation or source")
    created_at = models.DateTimeField(default=timezone.now)
    MODEL_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    model_type = models.CharField(max_length=10, choices=MODEL_TYPE_CHOICES, default='image')

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

class ModelVersion(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=50)
    resolution = models.IntegerField(help_text="Resolution in pixels")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    elo_rating = models.IntegerField(default=1500)  # Starting ELO rating
    is_api_implemented = models.BooleanField(default=False)
    tray_code = models.CharField(max_length=50, blank=True, help_text="Code used in tryon-tray package")
    price_per_inference = models.FloatField(default=0.04, help_text="Cost in USD per API call")
    model_type = models.CharField(max_length=10, choices=Model.MODEL_TYPE_CHOICES, default='image')

    def __str__(self):
        return f"{self.model.name} v{self.version}"

    class Meta:
        ordering = ['-elo_rating', '-created_at']

class InputSet(models.Model):
    name = models.CharField(max_length=200)
    garment_key = models.CharField(max_length=500, help_text="S3 key for garment image", null=True, blank=True)
    garment_thumb_key = models.CharField(max_length=500, help_text="S3 key for garment thumbnail", null=True, blank=True)
    model_key = models.CharField(max_length=500, help_text="S3 key for model image", null=True, blank=True)
    model_thumb_key = models.CharField(max_length=500, help_text="S3 key for model thumbnail", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='input_sets')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._s3_client = None

    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_S3_REGION_NAME
            )
        return self._s3_client

    def get_signed_url(self, key):
        if not key:
            return None
            
        # Maximum expiration time for presigned URLs (7 days in seconds)
        EXPIRATION = 7 * 24 * 60 * 60
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': key},
                ExpiresIn=EXPIRATION
            )
        except Exception as e:
            print(f"Error generating signed URL for key {key}: {str(e)}")
            return None

    @property
    def garment_image(self):
        return self.get_signed_url(self.garment_key)

    @property
    def model_image(self):
        return self.get_signed_url(self.model_key)

    @property
    def garment_thumbnail_url(self):
        return self.get_signed_url(self.garment_thumb_key)

    @property
    def model_thumbnail_url(self):
        return self.get_signed_url(self.model_thumb_key)

    def __str__(self):
        return self.name

class Tryon(models.Model):
    input_set = models.ForeignKey(InputSet, on_delete=models.CASCADE, related_name='tryons')
    model_version = models.ForeignKey(ModelVersion, on_delete=models.CASCADE, related_name='tryons')
    image_key = models.CharField(max_length=500, help_text="S3 key for tryon image", null=True, blank=True)
    thumb_key = models.CharField(max_length=500, help_text="S3 key for tryon thumbnail", null=True, blank=True)
    notes = models.CharField(max_length=500, help_text="Store notes as Text")
    created_at = models.DateTimeField(default=timezone.now)
    is_generated_by_api = models.BooleanField(default=False)
    time_taken = models.FloatField(null=True, blank=True, help_text="Time taken in seconds for API generation")
    resolution = models.CharField(max_length=20, help_text="Image resolution in format WIDTHxHEIGHT", null=True, blank=True)
    price_per_inference = models.FloatField(null=True, blank=True, help_text="Cost in USD for this inference")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._s3_client = None

    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_S3_REGION_NAME
            )
        return self._s3_client

    def get_signed_url(self, key):
        if not key:
            return None
            
        # Maximum expiration time for presigned URLs (7 days in seconds)
        EXPIRATION = 7 * 24 * 60 * 60
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': key},
                ExpiresIn=EXPIRATION
            )
        except Exception as e:
            print(f"Error generating signed URL for key {key}: {str(e)}")
            return None

    @property
    def image_path(self):
        return self.get_signed_url(self.image_key)

    @property
    def thumbnail_url(self):
        return self.get_signed_url(self.thumb_key)

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

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Reset token for {self.user.username}"

class RankedPair(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rankings')
    tryon_batch = models.ForeignKey('TryonBatch', on_delete=models.CASCADE, related_name='rankings')
    winner_tryon = models.ForeignKey('Tryon', on_delete=models.CASCADE, related_name='won_rankings')
    loser_tryon = models.ForeignKey('Tryon', on_delete=models.CASCADE, related_name='lost_rankings')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Rating tracking fields
    winner_rating_before = models.IntegerField(null=True)
    winner_rating_after = models.IntegerField(null=True)
    loser_rating_before = models.IntegerField(null=True)
    loser_rating_after = models.IntegerField(null=True)

    class Meta:
        unique_together = [['user', 'winner_tryon', 'loser_tryon']]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Store initial ratings
        self.winner_rating_before = self.winner_tryon.model_version.elo_rating
        self.loser_rating_before = self.loser_tryon.model_version.elo_rating

        # Calculate ELO rating changes
        K = 32  # K-factor for ELO calculation
        winner_rating = self.winner_rating_before
        loser_rating = self.loser_rating_before

        # Expected scores
        expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
        expected_loser = 1 - expected_winner

        # New ratings
        winner_new_rating = winner_rating + K * (1 - expected_winner)
        loser_new_rating = loser_rating + K * (0 - expected_loser)

        # Update ratings
        self.winner_tryon.model_version.elo_rating = round(winner_new_rating)
        self.loser_tryon.model_version.elo_rating = round(loser_new_rating)
        
        # Store final ratings
        self.winner_rating_after = self.winner_tryon.model_version.elo_rating
        self.loser_rating_after = self.loser_tryon.model_version.elo_rating
        
        # Save model versions
        self.winner_tryon.model_version.save()
        self.loser_tryon.model_version.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s ranking: {self.winner_tryon.model_version} > {self.loser_tryon.model_version}"

    @property
    def winner_rating_change(self):
        if self.winner_rating_before is not None and self.winner_rating_after is not None:
            return self.winner_rating_after - self.winner_rating_before
        return None

    @property
    def loser_rating_change(self):
        if self.loser_rating_before is not None and self.loser_rating_after is not None:
            return self.loser_rating_after - self.loser_rating_before
        return None
