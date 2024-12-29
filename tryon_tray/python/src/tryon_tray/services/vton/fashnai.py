"""Fashn.ai virtual try-on service."""

import requests
import time
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, Union

from ...base.vton import BaseVTON
from ...utils.config import get_env_or_raise
from ...utils.file_io import base64_with_prefix

class FashnaiVTON(BaseVTON):
    """Fashn.ai virtual try-on service."""
    
    BASE_URL = "https://api.fashn.ai/v1"
    
    def __init__(self, model_image, garment_image, **kwargs):
        super().__init__(model_image, garment_image, **kwargs)
        self.api_key = get_env_or_raise("FASHNAI_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.prediction_id = None
        self.start_time = None
        self.end_time = None
        self.time_taken = None
    
    def prepare_payload(self) -> Dict[str, Any]:
        """Prepare API request payload."""
        return {
            "model_image": base64_with_prefix(self.model_image),
            "garment_image": base64_with_prefix(self.garment_image),
            "category": self.params.get("category", "tops"),
            "mode": self.params.get("mode", "quality"),
            "nsfw_filter": self.params.get("nsfw_filter", True),
            "cover_feet": self.params.get("cover_feet", False),
            "adjust_hands": self.params.get("adjust_hands", False),
            "restore_background": self.params.get("restore_background", False),
            "restore_clothes": self.params.get("restore_clothes", False),
            "garment_photo_type": self.params.get("garment_photo_type", "auto"),
            "long_top": self.params.get("long_top", False),
            "seed": self.params.get("seed", 42),
            "num_samples": self.params.get("num_samples", 1)
        }
    
    def run(self) -> str:
        """Start the try-on process.
        
        Returns:
            str: Prediction ID for status checking
        """
        self.start_time = datetime.now()
        payload = self.prepare_payload()
        
        response = requests.post(
            f"{self.BASE_URL}/run",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        self.prediction_id = data["id"]
        self.status = "processing"
        return self.prediction_id
    
    def check_status(self) -> Tuple[bool, Optional[Union[list[str], Exception]]]:
        """Check current status of the try-on job.
        
        Returns:
            Tuple containing:
            - bool: Whether the job is complete
            - Optional[Union[list[str], Exception]]: Result URLs or error
        """
        response = requests.get(
            f"{self.BASE_URL}/status/{self.prediction_id}",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "completed":
            self.result_urls = data["output"]
            self.end_time = datetime.now()
            self.time_taken = int((self.end_time - self.start_time).total_seconds())
            return True, self.result_urls
        elif data["status"] == "failed":
            return True, Exception(f"Try-on failed: {data.get('error', 'Unknown error')}")
        
        return False, None
    
    def get_result(self) -> Dict[str, Any]:
        """Get the try-on result."""
        if not self.result_urls:
            raise ValueError("No result available. Run the try-on first.")
            
        result = {
            "urls": self.result_urls,
            "source_images": {
                "model": self.model_image,
                "garment": self.garment_image
            },
            "category": self.params.get("category", "tops"),
            "mode": self.params.get("mode", "quality"),
            "timing": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "time_taken": self.time_taken
            }
        }
        
        if self.auto_download and self.download_path:
            result["local_path"] = self.download_path
            
        return result 