import boto3
from io import BytesIO
from PIL import Image
import requests
from tryon_tray.api.vton import VTON
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
from tryon_tray.api.video_gen import generate_video
from tryon_tray.types.video import VideoMode, VideoDuration
from datetime import timedelta
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
    
    # Call tryon-tray API with model-specific parameters
    api_params = {
        'model_image': temp_model,
        'garment_image': temp_garment,
        'model_name': model_version.tray_code,
        'auto_download': True,
        'download_path': temp_result,
        'show_polling_progress': True,
    }
    
    # Add model-specific parameters
    if model_version.tray_code == 'replicate':
        api_params.update({
            'category': 'upper_body',
            'steps': 30,
            'seed': 42,
            'crop': False,
            'force_dc': False,
            'mask_only': False,
        })
        api_params.update({
            'garment_image': input_set.garment_image,
            'model_image': input_set.model_image,
        })
    elif model_version.tray_code in ['fashnai', 'klingai']:
        api_params.update({
            'category': 'tops',
            'mode': 'quality'
        })
    
    # Generate try-on
    result = VTON(**api_params)
    
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
    from pprint import pprint
    pprint(result)
    
    # Extract time taken in seconds
    time_taken = None
    if result.get('timing'):
        try:
            # Convert time_taken to seconds if it's a datetime.timedelta
            time_taken = result['timing']['time_taken'].total_seconds()
        except AttributeError:
            # If it's already a number, use it as is
            time_taken = float(result['timing']['time_taken'])
    
    return image_key, thumb_key, resolution, time_taken 

def generate_video_via_api(input_set, model_version, s3_client):
    """
    Generate a video using the tryon-tray API.
    Returns the S3 key for the generated video and the time taken.
    """
    # Download model image from S3
    model_obj = BytesIO()
    s3_client.download_fileobj(AWS_STORAGE_BUCKET_NAME, input_set.model_key, model_obj)
    model_obj.seek(0)
    temp_model = f"/tmp/{uuid.uuid4()}.jpg"
    with open(temp_model, 'wb') as f:
        f.write(model_obj.read())

    # Call video generation API
    result = generate_video(
        source_image=temp_model,
        prompt=input_set.prompt,
        mode=VideoMode.STANDARD.value,
        duration=VideoDuration.FIVE.value,
        show_polling_progress=True,
        auto_download=True,
        download_path=f"/tmp/{uuid.uuid4()}.mp4",
    )

    # Generate unique filename for S3
    timestamp = uuid.uuid4().hex[:8]
    video_key = f'tryons/{timestamp}_{model_version.model.name}_{model_version.version}.mp4'

    # Upload video to S3
    with open(result.local_path, 'rb') as f:
        s3_client.upload_fileobj(f, AWS_STORAGE_BUCKET_NAME, video_key)

    # Clean up temporary files
    import os
    os.remove(temp_model)
    os.remove(result.local_path)

    # Extract time taken in seconds
    time_taken = None
    if result.timing:
        try:
            # If time_taken is a string, convert it to a timedelta
            if isinstance(result.timing['time_taken'], str):
                time_taken = timedelta(seconds=float(result.timing['time_taken'].split(':')[-1])).total_seconds()
            else:
                time_taken = result.timing['time_taken'].total_seconds()
        except AttributeError:
            # If it's already a number, use it as is
            time_taken = float(result.timing['time_taken'])

    return video_key, time_taken 