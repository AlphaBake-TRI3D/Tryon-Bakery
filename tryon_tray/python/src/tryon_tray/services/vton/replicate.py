"""Replicate virtual try-on service."""

import replicate
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, Union, List

from ...base.vton import BaseVTON
from ...utils.config import get_replicate_api_token

class ReplicateVTON(BaseVTON):
    """Replicate virtual try-on service using IDM-VTON model."""
    
    MODEL_ID = "cuuupid/idm-vton:c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d021d3ff4"

    def __init__(self, model_image, garment_image, **kwargs):
        """Initialize Replicate VTON service.
        
        Note: model_image and garment_image must be URLs accessible by Replicate.
        Local file paths are not supported by Replicate's API.
        """
        super().__init__(model_image, garment_image, **kwargs)
        if not self.api_key:
            self.api_key = get_replicate_api_token()
        replicate.Client(api_token=self.api_key)
        self._prediction = None
        self.start_time = None
        self.end_time = None
        self.time_taken = None

    def run(self) -> str:
        """Run the try-on process and get results directly.
        
        Returns:
            str: Prediction ID (not used for Replicate)
            
        Raises:
            ValueError: If input images are not URLs
        """
        # Validate URLs
        if not (self.model_image.startswith('http://') or self.model_image.startswith('https://')):
            raise ValueError("Replicate requires model_image to be a URL. Local file paths are not supported. Please provide a publicly accessible URL.")
        if not (self.garment_image.startswith('http://') or self.garment_image.startswith('https://')):
            raise ValueError("Replicate requires garment_image to be a URL. Local file paths are not supported. Please provide a publicly accessible URL.")
        
        self.start_time = datetime.now()
        try:
            output = replicate.run(
                self.MODEL_ID,
                input={
                    "crop": self.params.get("crop", False),
                    "seed": self.params.get("seed", 42),
                    "steps": self.params.get("steps", 30),
                    "category": self.params.get("category", "upper_body"),
                    "force_dc": self.params.get("force_dc", False),
                    "human_img": self.model_image,
                    "garm_img": self.garment_image,
                    "mask_only": self.params.get("mask_only", False),
                    "garment_des": self.params.get("garment_des", "")
                }
            )
            self.status = "processing"
            self.end_time = datetime.now()
            self.time_taken = int((self.end_time - self.start_time).total_seconds())
            
            # Handle FileOutput object
            if hasattr(output, 'read'):
                # If it's a FileOutput object, save it directly
                if self.auto_download and self.download_path:
                    os.makedirs(os.path.dirname(self.download_path), exist_ok=True)
                    with open(self.download_path, 'wb') as f:
                        f.write(output.read())
                # Store the URL for consistency
                self.result_urls = [output.url]
            else:
                # If it's a URL or list of URLs
                self.result_urls = [output] if isinstance(output, str) else output
            
            # Return a dummy ID since Replicate is synchronous
            return "replicate_direct"
        except Exception as e:
            raise Exception(f"Replicate run failed: {str(e)}")

    def check_status(self) -> Tuple[bool, Optional[Union[List[str], Exception]]]:
        """Check status - not used for Replicate as it returns results directly.
        
        Returns:
            Tuple containing:
            - bool: Always True as results are immediate
            - Optional[Union[List[str], Exception]]: Result URLs
        """
        if not self.result_urls:
            return True, Exception("No results available")
        return True, self.result_urls
    
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
            "category": self.params.get("category", "upper_body"),
            "steps": self.params.get("steps", 30),
            "seed": self.params.get("seed", 42),
            "timing": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "time_taken": self.time_taken
            }
        }
        
        if self.auto_download and self.download_path:
            result["local_path"] = self.download_path
            
        return result 