"""Alphabake API client implementation."""

import os
import time
import json
import base64
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

class AlphabakeAPIClient:
    """Client for interacting with the Alphabake API."""
    
    def __init__(self, api_key: str, base_url: str = "https://loras-main.tri3d.in/"):
        """Initialize the Alphabake API client."""
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.create_url = f"{self.base_url}api/tryon/"
        self.fetch_url = f"{self.base_url}api/tryon_state/"
    
    def create_job(
        self,
        model_image_path: str,
        garment_image_path: str,
        mode: str = "balanced",
        garment_name: str = None,
        tryon_name: str = None
    ) -> str:
        """Create a virtual try-on job."""
        # Generate default names if not provided
        if not garment_name:
            garment_name = f"garment-{int(time.time())}"
        if not tryon_name:
            tryon_name = f"tryon-{int(time.time())}"
        
        # Read and encode images
        with open(model_image_path, 'rb') as f:
            human_image_data = f.read()
        with open(garment_image_path, 'rb') as f:
            garment_image_data = f.read()
            
        human_base64_image = base64.b64encode(human_image_data).decode('utf-8')
        garment_base64_image = base64.b64encode(garment_image_data).decode('utf-8')
        
        # Prepare payload
        payload = {
            'human_image_base64': human_base64_image,
            'garment_image_base64': garment_base64_image,
            'garment_name': garment_name,
            'tryon_name': tryon_name,
            'mode': mode  # Options: 'fast', 'balanced', or 'quality'
        }
        
        # Make API request
        response = requests.post(
            self.create_url,
            headers=self.headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        
        # Return the tryon_pk for status tracking
        return response.json()["tryon_pk"]
    
    def fetch_job(
        self,
        tryon_pk: str,
        max_attempts: int = 60,
        delay: int = 2
    ) -> List[str]:
        """Fetch the job status and results."""
        payload = {
            'tryon_pk': tryon_pk
        }
        
        time_elapsed = 0
        for _ in range(max_attempts):
            response = requests.post(
                self.fetch_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            result = response.json()
            
            # Check if processing is complete
            if result.get("status") == "done":
                return [result.get("s3_url")]
            elif result.get("message") != "success":
                raise Exception(f"Tryon processing failed: {result.get('message')}")
            
            # Wait before next attempt
            time.sleep(delay)
            time_elapsed += delay
            
        raise TimeoutError(f"Maximum polling time exceeded: {time_elapsed} seconds")
    
    def download_image(self, url: str, output_path: str) -> None:
        """Download the generated image."""
        response = requests.get(url)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content) 