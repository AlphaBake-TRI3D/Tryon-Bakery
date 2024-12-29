"""Types for virtual try-on services."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class VTONProvider(Enum):
    """Available VTON providers."""
    FASHNAI = "fashnai"
    KLINGAI = "klingai"
    REPLICATE = "replicate"

class VTONMode(Enum):
    """VTON generation modes."""
    QUALITY = "quality"
    SPEED = "speed"

class VTONCategory(Enum):
    """Supported garment categories."""
    TOPS = "tops"
    DRESSES = "dresses"
    FULL_BODY = "full_body"
    UPPER_BODY = "upper_body"

@dataclass
class VTONParams:
    """Parameters for virtual try-on."""
    model_image: str
    garment_image: str
    provider: str = VTONProvider.FASHNAI.value
    mode: str = VTONMode.QUALITY.value
    category: str = VTONCategory.TOPS.value
    auto_download: bool = False
    download_path: Optional[str] = None
    show_polling_progress: bool = False
    seed: Optional[int] = None

@dataclass
class VTONResponse:
    """Response from virtual try-on."""
    urls: list[str]
    source_images: Dict[str, str]
    mode: str
    category: str
    local_path: Optional[str] = None
    timing: Optional[Dict[str, Any]] = None

class VTONError(Exception):
    """Error from virtual try-on."""
    def __init__(self, status_code: int, service_code: str, message: str):
        self.status_code = status_code
        self.service_code = service_code
        self.message = message
        super().__init__(f"[{status_code}] {service_code}: {message}") 