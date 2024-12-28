import replicate
from ..base import BaseVTON
from ..utils.config import get_replicate_api_token

class ReplicateVTON(BaseVTON):
    MODEL_ID = "cuuupid/idm-vton:c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d021d3ff4"

    def __init__(self, model_image, garment_image, **kwargs):
        super().__init__(model_image, garment_image, **kwargs)
        if not self.api_key:
            self.api_key = get_replicate_api_token()
        replicate.Client(api_token=self.api_key)
        self._prediction = None

    def run(self):
        """Replicate is synchronous from Python's perspective"""
        try:
            self._prediction = replicate.run(
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
            return self._prediction
        except Exception as e:
            return True, Exception(f"Replicate run failed: {str(e)}")

    def check_status(self):
        """
        Since Replicate's run is synchronous, we return completed immediately
        with the result from run()
        """
        if self._prediction is None:
            return True, Exception("No prediction found. Did run() fail?")
            
        # Convert single URL to list for consistency
        result = [self._prediction] if isinstance(self._prediction, str) else self._prediction
        return True, result 