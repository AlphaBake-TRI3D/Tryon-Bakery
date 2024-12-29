"""File I/O utilities."""

import base64
import os
import requests
from pathlib import Path
from typing import Union, Optional

def image_to_base64(image_path: Union[str, Path]) -> str:
    """Convert image to base64 string.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Base64 encoded image string
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def base64_with_prefix(image_path: Union[str, Path]) -> str:
    """Convert image to base64 string with data URI prefix.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Base64 encoded image string with data URI prefix
    """
    ext = Path(image_path).suffix.lower()
    mime_type = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif'
    }.get(ext, 'image/jpeg')
    
    return f"data:{mime_type};base64,{image_to_base64(image_path)}"

def download_file(url: str, output_path: Union[str, Path], chunk_size: int = 8192) -> Optional[str]:
    """Download file from URL to specified path.
    
    Args:
        url: URL to download from
        output_path: Path to save file to
        chunk_size: Size of chunks to download
        
    Returns:
        Path to downloaded file if successful, None otherwise
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        return str(output_path)
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None 