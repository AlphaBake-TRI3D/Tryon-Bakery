"""Alphabake virtual try-on service."""

import os
import time
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, Union, List

from ...base.vton import BaseVTON
from ...api.alphabake import AlphabakeAPIClient
from ...utils.config import get_alphabake_api_token

class AlphabakeVTON(BaseVTON):
    """Alphabake virtual try-on service implementation."""
    
    def __init__(self, model_image: str, garment_image: str, **kwargs):
        """Initialize Alphabake VTON service."""
        super().__init__(model_image, garment_image, **kwargs)
        if not self.api_key:
            self.api_key = get_alphabake_api_token()
        
        base_url = kwargs.get("base_url", "https://loras-main.tri3d.in/")
        self.client = AlphabakeAPIClient(api_key=self.api_key, base_url=base_url)
        self._tryon_pk = None
        self.start_time = None
        self.end_time = None
        self.time_taken = None
        
    def run(self) -> str:
        """Run the try-on process."""
        # Validate image paths
        if not os.path.exists(self.model_image):
            raise ValueError(f"Model image not found: {self.model_image}")
        if not os.path.exists(self.garment_image):
            raise ValueError(f"Garment image not found: {self.garment_image}")
        
        self.start_time = datetime.now()
        try:
            self._tryon_pk = self.client.create_job(
                model_image_path=self.model_image,
                garment_image_path=self.garment_image,
                mode=self.params.get("mode", "balanced"),
                garment_name=self.params.get("garment_name"),
                tryon_name=self.params.get("tryon_name")
            )
            self.status = "processing"
            return self._tryon_pk
        except Exception as e:
            raise Exception(f"Alphabake job creation failed: {str(e)}")
    
    def check_status(self) -> Tuple[bool, Optional[Union[List[str], Exception]]]:
        """Check the status of the try-on process."""
        if not self._tryon_pk:
            return True, Exception("No tryon_pk available. Run the try-on first.")
        
        try:
            self.result_urls = self.client.fetch_job(
                self._tryon_pk,
                max_attempts=self.params.get("max_attempts", 60),
                delay=self.params.get("delay", 2)
            )
            self.status = "completed"
            self.end_time = datetime.now()
            self.time_taken = (self.end_time - self.start_time).total_seconds()
            
            # Download if auto_download is enabled
            if self.auto_download and self.download_path and self.result_urls:
                self.client.download_image(self.result_urls[0], self.download_path)
            
            return True, self.result_urls
        except TimeoutError:
            return False, None
        except Exception as e:
            return True, Exception(f"Alphabake job check failed: {str(e)}")
    
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
            "mode": self.params.get("mode", "balanced"),
            "timing": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "time_taken": int(self.time_taken) if self.time_taken else None
            }
        }
        
        if self.auto_download and self.download_path:
            result["local_path"] = self.download_path
            
        return result 