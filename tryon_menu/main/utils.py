import boto3
from io import BytesIO
from PIL import Image
import requests
from tryon_tray.vton_api import VTON
from django.conf import settings
from .models import InputSet, ModelVersion, Tryon
import uuid
from tryon_menu.aws_constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME
)
from dotenv import load_dotenv
load_dotenv()

def generate_tryon_via_api(input_set, model_version, s3_client):
    """
    Generate a tryon image using the tryon-tray API.
    Returns the S3 keys for the generated image and its thumbnail, along with metadata.
    """
    # Download input images from S3
    garment_obj = BytesIO()
    model_obj = BytesIO()
    
    s3_client.download_fileobj(AWS_STORAGE_BUCKET_NAME, input_set.garment_key, garment_obj)
    s3_client.download_fileobj(AWS_STORAGE_BUCKET_NAME, input_set.model_key, model_obj)
    
    # Save temporary files
    garment_obj.seek(0)
    model_obj.seek(0)
    
    temp_garment = f"/tmp/{uuid.uuid4()}.jpg"
    temp_model = f"/tmp/{uuid.uuid4()}.jpg"
    temp_result = f"/tmp/{uuid.uuid4()}.jpg"
    
    with open(temp_garment, 'wb') as f:
        f.write(garment_obj.read())
    with open(temp_model, 'wb') as f:
        f.write(model_obj.read())
    
    # Call tryon-tray API
    result = VTON(
        model_image=temp_model,
        garment_image=temp_garment,
        model_name=model_version.tray_code,
        auto_download=True,
        download_path=temp_result,
        show_polling_progress=True,
    )
    
    # Generate unique filenames for S3
    timestamp = uuid.uuid4().hex[:8]
    
    # Create S3 keys
    image_key = f'tryons/{timestamp}_{model_version.model.name}_{model_version.version}.jpg'
    thumb_key = f'thumbnails/tryons/{timestamp}_{model_version.model.name}_{model_version.version}_thumb.jpg'
    
    # Get image resolution
    with Image.open(temp_result) as img:
        width, height = img.size
        resolution = f"{width}x{height}"
        
        # Create thumbnail
        img.thumbnail((600, 600))
        thumb_buffer = BytesIO()
        img.save(thumb_buffer, format='JPEG')
        thumb_buffer.seek(0)
        
        # Upload thumbnail
        s3_client.upload_fileobj(thumb_buffer, AWS_STORAGE_BUCKET_NAME, thumb_key)
    
    # Upload original image
    with open(temp_result, 'rb') as f:
        s3_client.upload_fileobj(f, AWS_STORAGE_BUCKET_NAME, image_key)
    
    # Clean up temporary files
    import os
    os.remove(temp_garment)
    os.remove(temp_model)
    os.remove(temp_result)
    
    # Extract time taken in seconds
    time_taken = None
    if result.get('timing') and result['timing'].get('time_taken'):
        try:
            # Convert time_taken to seconds if it's a datetime.timedelta
            time_taken = result['timing']['time_taken'].total_seconds()
        except AttributeError:
            # If it's already a number, use it as is
            time_taken = float(result['timing']['time_taken'])
    
    return image_key, thumb_key, resolution, time_taken 