"""VModel API client implementation."""

import os
import time
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

class VModelAPIClient:
    """Client for interacting with the VModel API."""
    
    BASE_URL = "https://developer.vmodel.ai/api/vmodel/v1/ai-virtual-try-on"
    
    def __init__(self, api_key: str):
        """Initialize the VModel API client."""
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key,
            "accept": "application/json"
        }
    
    def create_job(
        self,
        model_image_path: str,
        garment_image_path: str,
        clothes_type: str = "upper_body",
        prompt: str = ""
    ) -> str:
        """Create a virtual try-on job."""
        files = [
            ('clothes_image', (os.path.basename(garment_image_path), open(garment_image_path, 'rb'), 'image/png')),
            ('custom_model', (os.path.basename(model_image_path), open(model_image_path, 'rb'), 'image/png'))
        ]
        
        payload = {
            'clothes_type': clothes_type,
            'prompt': prompt
        }
        
        response = requests.post(
            f"{self.BASE_URL}/create-job",
            headers=self.headers,
            data=payload,
            files=files
        )
        response.raise_for_status()
        
        return response.json()["result"]["job_id"]
    
    def fetch_job(
        self,
        job_id: str,
        max_attempts: int = 60,
        delay: int = 5
    ) -> List[str]:
        """Fetch the job status and results."""
        for _ in range(max_attempts):
            response = requests.get(
                f"{self.BASE_URL}/get-job/{job_id}",
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            if result["code"] == 100000 and result["result"]["output_image_url"]:
                return result["result"]["output_image_url"]
            elif result["code"] == 300104:
                raise Exception("Image generation failed.")
            
            time.sleep(delay)
        
        raise TimeoutError("Maximum polling attempts reached")
    
    def download_image(self, url: str, output_path: str) -> None:
        """Download the generated image."""
        response = requests.get(url)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content) 