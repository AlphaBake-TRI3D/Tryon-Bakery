import os
import boto3
import io
from PIL import Image
import json
from dotenv import load_dotenv

load_dotenv()

def find_image_file(directory, base_name):
    """Find image file with supported extensions in the directory."""
    supported_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    for ext in supported_extensions:
        file_path = os.path.join(directory, f"{base_name}{ext}")
        if os.path.exists(file_path):
            return file_path
    return None

def upload_to_s3(file_bytes, bucket, key, aws_access_key_id, aws_secret_access_key, aws_session_token=None, region_name='us-east-1'):
    if aws_session_token:
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name
        )
    else:
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
    s3.put_object(Bucket=bucket, Key=key, Body=file_bytes)

def get_public_url(bucket, key, region_name='us-east-1'):
    return f"https://{bucket}.s3.{region_name}.amazonaws.com/{key}"

def resize_to_max_dimension(img, max_dim=1024):
    """Resize image so the largest dimension is max_dim, keeping aspect ratio."""
    width, height = img.size
    if max(width, height) <= max_dim:
        return img
    if width > height:
        new_width = max_dim
        new_height = int(max_dim * height / width)
    else:
        new_height = max_dim
        new_width = int(max_dim * width / height)
    return img.resize((new_width, new_height), Image.LANCZOS)

aws_access_key_id = os.getenv('AWSAccessKeyId')
aws_secret_access_key = os.getenv('AWSSecretKey')
aws_session_token = os.getenv('AWS_SESSION_TOKEN')  # Optional
if not aws_session_token:
    aws_session_token = None
bucket = os.getenv('AWSBucketName','alpha-bake-loras')
region_name = os.getenv('AWSRegion', 'us-east-1')

input_key = '5pairs-v-small'
input_dir = f'inputs/5pairs-v-small'
OUTPUT_DIR = 'outputs/'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
output_json_path = f'{OUTPUT_DIR}/5pairs-v-small.json'




output_json = {}

for cur_folder in os.listdir(input_dir):
    if '.DS_Store' in cur_folder:
        continue
    cur_dir = os.path.join(input_dir, cur_folder)

    if not os.path.isdir(cur_dir):
        continue

    human_image_path = find_image_file(cur_dir, 'human')
    garment_image_path = find_image_file(cur_dir, 'garment')
    
    if not human_image_path or not garment_image_path:
        print(f"Skipping {cur_folder}: Missing human or garment image")
        continue

    json_path = os.path.join(cur_dir, 'tryon_params.json')
    with open(json_path, 'r') as f:
        tryon_params = json.load(f)
    garment_type = tryon_params['garment']['garment_type']
    
    with open(human_image_path, "rb") as f:
        human_img = Image.open(f)
        if human_img.mode != "RGB":
            human_img = human_img.convert("RGB")
        human_img = resize_to_max_dimension(human_img, 1536)
        buffer = io.BytesIO()
        
        human_img.save(buffer, format="JPEG", quality=95)
        human_img_bytes = buffer.getvalue()

    human_key = f"Scale/{input_key}/{cur_folder}/human.jpg"
    upload_to_s3(human_img_bytes, bucket, human_key, aws_access_key_id, aws_secret_access_key, aws_session_token, region_name)
    human_public_url = get_public_url(bucket, human_key, region_name)

    with open(garment_image_path, "rb") as f:
        garment_img = Image.open(f)
        if garment_img.mode != "RGB":
            garment_img = garment_img.convert("RGB")
        garment_img = resize_to_max_dimension(garment_img, 1024)
        buffer = io.BytesIO()
        garment_img.save(buffer, format="JPEG", quality=95)
        garment_img_bytes = buffer.getvalue()

    garment_key = f"Scale/{input_key}/{cur_folder}/garment.jpg"
    upload_to_s3(garment_img_bytes, bucket, garment_key, aws_access_key_id, aws_secret_access_key, aws_session_token, region_name)
    garment_public_url = get_public_url(bucket, garment_key, region_name)

    output_json[cur_folder] = {
        'human_url': human_public_url,
        'garment_url': garment_public_url,
        'garment_type': garment_type
    }
    print(f"Uploaded {cur_folder} to S3")

with open(output_json_path, 'w') as f:
    json.dump(output_json, f, indent=4)
