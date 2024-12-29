from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class VideoModelVersion(Enum):
    """Available video model versions."""
    KLING_V1 = "kling-v1"
    KLING_V1_5 = "kling-v1-5"

class VideoMode(Enum):
    """Video generation modes."""
    STANDARD = "std"
    PROFESSIONAL = "pro"

class VideoDuration(Enum):
    """Supported video durations in seconds."""
    FIVE = "5"
    TEN = "10"

@dataclass
class VideoGenParams:
    """Parameters for video generation."""
    source_image: str
    prompt: str
    model_name: str = VideoModelVersion.KLING_V1_5.value
    mode: str = VideoMode.STANDARD.value
    duration: str = VideoDuration.FIVE.value
    negative_prompt: str = ""
    cfg_scale: float = 0.5
    seed: Optional[int] = None
    auto_download: bool = False
    download_path: Optional[str] = None
    show_polling_progress: bool = False

@dataclass
class VideoGenResponse:
    """Response from video generation."""
    video_url: str
    source_image: str
    prompt: str
    mode: str
    duration: str
    task_id: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    local_path: Optional[str] = None
    timing: Optional[Dict[str, Any]] = None

class VideoGenError(Exception):
    """Error from video generation."""
    def __init__(self, status_code: int, service_code: str, message: str):
        self.status_code = status_code
        self.service_code = service_code
        self.message = message
        super().__init__(f"[{status_code}] {service_code}: {message}") 