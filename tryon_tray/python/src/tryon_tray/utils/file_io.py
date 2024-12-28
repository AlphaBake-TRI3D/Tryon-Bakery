import base64
import os
import requests
from pathlib import Path

def image_to_base64(image_path: str) -> str:
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

def base64_with_prefix(image_path: str) -> str:
    """Convert image to base64 string with data URI prefix"""
    return f"data:image/jpeg;base64,{image_to_base64(image_path)}"

def download_image(url: str, output_path: str):
    """Download image from URL to local path"""
    response = requests.get(url)
    response.raise_for_status()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content) 