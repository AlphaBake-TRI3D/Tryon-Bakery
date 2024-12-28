import requests
import time
from ..base import BaseVTON
from ..utils.config import get_fashnai_api_key
from ..utils.file_io import base64_with_prefix

class FashnaiVTON(BaseVTON):
    BASE_URL = "https://api.fashn.ai/v1"

    def __init__(self, model_image, garment_image, **kwargs):
        super().__init__(model_image, garment_image, **kwargs)
        if not self.api_key:
            self.api_key = get_fashnai_api_key()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def run(self):
        payload = {
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

        response = requests.post(f"{self.BASE_URL}/run", headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        self.prediction_id = data["id"]
        self.status = "processing"
        return self.prediction_id

    def check_status(self):
        """Check current status of the Fashn.ai job"""
        response = requests.get(
            f"{self.BASE_URL}/status/{self.prediction_id}",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "completed":
            return True, data["output"]
        elif data["status"] == "failed":
            return True, Exception(f"Prediction failed: {data.get('error')}")
        
        return False, None 