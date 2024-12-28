import requests
import time
import jwt
from ..base import BaseVTON
from ..utils.config import get_klingai_credentials
from ..utils.file_io import image_to_base64

class KlingaiVTON(BaseVTON):
    BASE_URL = "https://api.klingai.com/v1/images"

    def __init__(self, model_image, garment_image, **kwargs):
        super().__init__(model_image, garment_image, **kwargs)
        self.access_id, self.api_key = get_klingai_credentials()
        self.headers = {
            "Content-Type": "application/json"
        }

    def _get_jwt_token(self):
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

    def run(self):
        self.headers["Authorization"] = f"Bearer {self._get_jwt_token()}"
        
        payload = {
            "model_name": "kolors-virtual-try-on-v1",
            "human_image": image_to_base64(self.model_image),
            "cloth_image": image_to_base64(self.garment_image),
            "callback_url": ""
        }

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

    def check_status(self):
        """Check current status of the Kling.ai job"""
        # Refresh JWT token for each status check
        self.headers["Authorization"] = f"Bearer {self._get_jwt_token()}"
        
        response = requests.get(
            f"{self.BASE_URL}/kolors-virtual-try-on/{self.prediction_id}",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data["data"]["task_status"] == "succeed":
            return True, [img["url"] for img in data["data"]["task_result"]["images"]]
        elif data["data"]["task_status"] == "failed":
            return True, Exception(f"Task failed: {data['data']['task_status_msg']}")
        
        return False, None 