"""Base class for video generation services."""

from abc import abstractmethod
from typing import Dict, Any, Optional
import time
from datetime import datetime
from pathlib import Path
import requests

from .service import BaseService
from ..utils.file_io import download_file

class BaseVideoGen(BaseService):
    """Base class for video generation services."""
    
    def __init__(
        self,
        source_image: str,
        prompt: str,
        model_name: str = "kling-v1-5",
        mode: str = "std",
        duration: str = "5",
        negative_prompt: str = "",
        cfg_scale: float = 0.5,
        seed: Optional[int] = None,
        auto_download: bool = False,
        download_path: Optional[str] = None,
        show_polling_progress: bool = False,
        **kwargs
    ):
        """Initialize video generation service.
        
        Args:
            source_image: Path or URL to the source image
            prompt: Text description of desired video
            model_name: Name of the model to use
            mode: Generation mode (e.g., "standard" or "professional")
            duration: Video duration in seconds
            negative_prompt: What to avoid in generation
            cfg_scale: Control strength of the prompt
            seed: Random seed for reproducibility
            auto_download: Whether to automatically download the generated video
            download_path: Path to save the downloaded video
            show_polling_progress: Whether to show polling progress
            **kwargs: Additional service-specific parameters
        """
        super().__init__(**kwargs)
        self.source_image = source_image
        self.prompt = prompt
        self.model_name = model_name
        self.mode = mode
        self.duration = duration
        self.negative_prompt = negative_prompt
        self.cfg_scale = cfg_scale
        self.seed = seed
        self.result_url = None
        self.auto_download = auto_download
        self.download_path = download_path
        self.show_polling_progress = show_polling_progress
        self.start_time = None
        self.end_time = None
        self.time_taken = None
        
    def _print_polling_progress(self):
        """Print polling progress if enabled."""
        if self.show_polling_progress:
            print(".", end="", flush=True)
    
    def _download_video(self) -> str:
        """Download the generated video."""
        if not self.result_url:
            raise ValueError("No video URL available")
            
        if not self.download_path:
            # Generate default path if none provided
            timestamp = int(time.time())
            self.download_path = f"outputs/video_{timestamp}.mp4"
            
        # Ensure directory exists
        Path(self.download_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Download the file
        download_file(self.result_url, self.download_path)
        return self.download_path
        
    @abstractmethod
    def validate_parameters(self) -> None:
        """Validate service-specific parameters."""
        pass
    
    @abstractmethod
    def prepare_payload(self) -> Dict[str, Any]:
        """Prepare the API request payload."""
        pass
    
    @abstractmethod
    def process_response(self, response: Dict[str, Any]) -> str:
        """Process API response and return video URL."""
        pass
    
    def get_result(self) -> Dict[str, Any]:
        """Get the generation result."""
        if not self.result_url:
            raise ValueError("No result available. Run the generation first.")
            
        result = {
            "video_url": self.result_url,
            "source_image": self.source_image,
            "prompt": self.prompt,
            "mode": self.mode,
            "duration": self.duration,
            "timing": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "time_taken": str(self.time_taken) if self.time_taken else None
            }
        }
        
        # Add download path if auto-downloaded
        if self.auto_download and self.download_path:
            result["local_path"] = self.download_path
            
        return result 