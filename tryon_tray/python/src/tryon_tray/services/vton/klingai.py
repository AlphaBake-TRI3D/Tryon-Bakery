"""Kling.ai virtual try-on service."""

import requests
import time
import jwt
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, Union, List

from ...base.vton import BaseVTON
from ...utils.config import get_klingai_credentials
from ...utils.file_io import image_to_base64

class KlingaiVTON(BaseVTON):
    """Kling.ai virtual try-on service."""
    
    BASE_URL = "https://api.klingai.com/v1/images"

    def __init__(self, model_image, garment_image, **kwargs):
        super().__init__(model_image, garment_image, **kwargs)
        self.access_id, self.api_key = get_klingai_credentials()
        self.headers = {
            "Content-Type": "application/json"
        }
        self.prediction_id = None
        self.start_time = None
        self.end_time = None
        self.time_taken = None

    def _get_jwt_token(self):
        """Generate JWT token for authentication."""
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            "iss": self.access_id,
            "exp": int(time.time()) + 1800,
            "nbf": int(time.time()) - 5
        }
        return jwt.encode(payload, self.api_key, headers=headers)

    def prepare_payload(self) -> Dict[str, Any]:
        """Prepare API request payload."""
        return {
            "model_name": "kolors-virtual-try-on-v1",
            "human_image": image_to_base64(self.model_image),
            "cloth_image": image_to_base64(self.garment_image),
            "callback_url": ""
        }

    def run(self) -> str:
        """Start the try-on process.
        
        Returns:
            str: Prediction ID for status checking
        """
        self.start_time = datetime.now()
        self.headers["Authorization"] = f"Bearer {self._get_jwt_token()}"
        
        payload = self.prepare_payload()
        response = requests.post(
            f"{self.BASE_URL}/kolors-virtual-try-on", 
            headers=self.headers, 
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        self.prediction_id = data["data"]["task_id"]
        self.status = "processing"
        return self.prediction_id

    def check_status(self) -> Tuple[bool, Optional[Union[List[str], Exception]]]:
        """Check the status of the try-on process.
        
        Returns:
            Tuple containing:
            - bool: Whether the process is complete
            - Optional[Union[List[str], Exception]]: Result URLs or error
        """
        # Refresh JWT token for each status check
        self.headers["Authorization"] = f"Bearer {self._get_jwt_token()}"
        
        response = requests.get(
            f"{self.BASE_URL}/kolors-virtual-try-on/{self.prediction_id}",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data["data"]["task_status"] == "succeed":
            self.result_urls = [img["url"] for img in data["data"]["task_result"]["images"]]
            self.end_time = datetime.now()
            self.time_taken = int((self.end_time - self.start_time).total_seconds())
            return True, self.result_urls
        elif data["data"]["task_status"] == "failed":
            return True, Exception(f"Task failed: {data['data']['task_status_msg']}")
        
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
            "timing": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "time_taken": self.time_taken
            }
        }
        
        if self.auto_download and self.download_path:
            result["local_path"] = self.download_path
            
        return result 