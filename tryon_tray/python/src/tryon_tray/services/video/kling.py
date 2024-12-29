"""Kling AI video generation service."""

import time
import jwt
import base64
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from ...base.video import BaseVideoGen
from ...types.video import VideoModelVersion, VideoMode, VideoDuration, VideoGenError
from ...utils.config import get_env_or_raise

class KlingVideoGen(BaseVideoGen):
    """Kling AI video generation service."""
    
    BASE_URL = "https://api.klingai.com/v1"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_id = get_env_or_raise("KLINGAI_ACCESS_ID")
        self.api_key = get_env_or_raise("KLINGAI_API_KEY")
        self.task_id = None
        self.created_at = None
        self.updated_at = None
    
    def validate_parameters(self) -> None:
        """Validate Kling-specific parameters."""
        # Validate model version
        if not any(self.model_name == version.value for version in VideoModelVersion):
            raise ValueError(f"Invalid model version. Must be one of: {[m.value for m in VideoModelVersion]}")
        
        # Validate mode
        if not any(self.mode == mode.value for mode in VideoMode):
            raise ValueError(f"Invalid mode. Must be one of: {[m.value for m in VideoMode]}")
        
        # Validate duration
        if not any(self.duration == duration.value for duration in VideoDuration):
            raise ValueError(f"Invalid duration. Must be one of: {[d.value for d in VideoDuration]}")
    
    def _encode_jwt_token(self) -> str:
        """Generate JWT token for authentication."""
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            "iss": self.access_id,
            "exp": int(time.time()) + 1800,  # 30 minutes expiry
            "nbf": int(time.time()) - 5
        }
        return jwt.encode(payload, self.api_key, headers=headers)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self._encode_jwt_token()}",
            "Content-Type": "application/json"
        }
    
    def _image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def prepare_payload(self) -> Dict[str, Any]:
        """Prepare the API request payload."""
        source_base64 = self._image_to_base64(self.source_image)
        
        payload = {
            "model_name": self.model_name,
            "mode": self.mode,
            "duration": self.duration,
            "image": source_base64,
            "prompt": self.prompt,
            "cfg_scale": self.cfg_scale
        }
        
        if self.negative_prompt:
            payload["negative_prompt"] = self.negative_prompt
        if self.seed is not None:
            payload["seed"] = self.seed
            
        return payload
    
    def process_response(self, response: Dict[str, Any]) -> str:
        """Process API response and extract video URL."""
        videos = response["data"]["task_result"]["videos"]
        if not videos:
            raise ValueError("No videos in response")
            
        video_data = videos[0]
        self.result_url = video_data["url"]
        self.task_id = response["data"]["task_id"]
        self.created_at = response["data"].get("created_at")
        self.updated_at = response["data"].get("updated_at")
        
        return self.result_url
    
    def run(self) -> None:
        """Run the video generation process."""
        self.start_time = datetime.now()
        
        self.validate_parameters()
        payload = self.prepare_payload()
        
        # Create task
        response = requests.post(
            f"{self.BASE_URL}/videos/image2video",
            headers=self._get_headers(),
            json=payload
        )
        
        if not response.ok:
            self._handle_error(response)
        
        task_data = response.json()
        self.task_id = task_data["data"]["task_id"]
        
        # Poll for results
        max_attempts = 120
        delay = 5
        
        if self.show_polling_progress:
            print("\nPolling for results", end="", flush=True)
            
        for _ in range(max_attempts):
            self._print_polling_progress()
            
            response = requests.get(
                f"{self.BASE_URL}/videos/image2video/{self.task_id}",
                headers=self._get_headers()
            )
            
            if not response.ok:
                self._handle_error(response)
                
            result = response.json()
            status = result["data"]["task_status"]
            
            if status == "succeed":
                self.process_response(result)
                self.end_time = datetime.now()
                self.time_taken = self.end_time - self.start_time
                
                if self.auto_download:
                    self._download_video()
                return
            elif status == "failed":
                raise Exception(f"Task failed: {result['data'].get('task_status_msg', 'Unknown error')}")
            
            time.sleep(delay)
        
        raise TimeoutError("Maximum polling attempts reached")
    
    def _handle_error(self, response: requests.Response) -> None:
        """Handle API errors."""
        try:
            error_data = response.json()
            raise VideoGenError(
                status_code=response.status_code,
                service_code=error_data.get("code", "Unknown"),
                message=error_data.get("message", response.text)
            )
        except (ValueError, KeyError):
            raise VideoGenError(
                status_code=response.status_code,
                service_code="Unknown",
                message=response.text
            )
    
    def get_result(self) -> Dict[str, Any]:
        """Get the generation result with additional metadata."""
        result = super().get_result()
        result.update({
            "task_id": self.task_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        })
        return result 