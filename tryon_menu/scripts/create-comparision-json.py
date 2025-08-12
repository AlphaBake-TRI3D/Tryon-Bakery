import json
import os
import io
from PIL import Image
import boto3
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv('AWSAccessKeyId')
aws_secret_access_key = os.getenv('AWSSecretKey')
aws_session_token = os.getenv('AWS_SESSION_TOKEN')  # Optional
if not aws_session_token:
    aws_session_token = None
bucket = os.getenv('AWSBucketName','alpha-bake-loras')
region_name = os.getenv('AWSRegion', 'us-east-1')


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


def upload_block(image_path, s3_key):

    
    with open(image_path, "rb") as f:
        img = Image.open(f)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_bytes = buffer.getvalue()

    print(image_path)
    print(f"Size of img_bytes: {len(img_bytes)}")
    # url = upload_to_s3(img_bytes, bucket, s3_key, aws_access_key_id, aws_secret_access_key, aws_session_token, region_name)
    # presigned_url = generate_presigned_url(bucket, s3_key, aws_access_key_id, aws_secret_access_key, aws_session_token, region_name)
    url = upload_to_s3(img_bytes, bucket, s3_key, aws_access_key_id, aws_secret_access_key, aws_session_token, region_name)
    public_url = get_public_url(bucket, s3_key, region_name)
    return url, public_url


input_images_dir = 'inputs/200pairs-v3'
input_images_json_path = 'outputs/200pairs-v3.json'

input_images_json = json.load(open(input_images_json_path))


models_dict = {
    "alphabake-156-fast": 'inputs/alphabake-200-v3/',
    "google-preview-0804": 'inputs/200pairs-v3-google-preview-tryon/tryon/',
    "fashn-1.6-quality": 'inputs/fashn/',
}

s3_key_prefix = '200pairs-v3'

output_json_path = 'outputs/200pairs-v3-comparision.json'

comparision_json = {}
for cur_folder in input_images_json:
    print(cur_folder)
    comparision_json[cur_folder] = {
        'name' : cur_folder,
        'human' : input_images_json[cur_folder]['human_url'],
        'garment' : input_images_json[cur_folder]['garment_url'],
        'garment_type' : input_images_json[cur_folder]['garment_type'],
    }
    for model_name in models_dict:
        cur_path = models_dict[model_name] + cur_folder + '.jpg'
        if 'runwayml' in model_name or 'google-1.0' in model_name:
            cur_path = models_dict[model_name] + cur_folder + '.png'
        try:
            url, public_url = upload_block(cur_path, f'{s3_key_prefix}/{model_name}/{cur_folder}.jpg')
        except Exception as e:
            print(e)
            continue
        comparision_json[cur_folder][model_name] = public_url

with open(output_json_path, 'w') as f:
    json.dump(comparision_json, f, indent=4)











