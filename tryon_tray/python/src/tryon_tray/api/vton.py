"""Virtual try-on API."""

from typing import Dict, Any, Optional
from pathlib import Path
from ..services.factory import get_vton_service

def VTON(
    model_image: str,
    garment_image: str,
    model_name: str = "fashnai",
    auto_download: bool = False,
    download_path: Optional[str] = None,
    max_polling_attempts: int = 60,
    polling_interval: int = 5,
    show_polling_progress: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """Generate a virtual try-on image.
    
    Args:
        model_image: Path to the model/person image
        garment_image: Path to the garment image
        model_name: Name of the model to use (e.g., "fashnai", "replicate")
        auto_download: Whether to automatically download the result
        download_path: Path to save the downloaded image
        max_polling_attempts: Maximum number of polling attempts
        polling_interval: Time between polling attempts in seconds
        show_polling_progress: Whether to show polling progress
        **kwargs: Additional model-specific parameters
        
    Returns:
        Dictionary containing result URLs and metadata
    """
    # Get appropriate service
    service = get_vton_service(
        model_name=model_name,
        model_image=model_image,
        garment_image=garment_image,
        auto_download=auto_download,
        download_path=download_path,
        show_polling_progress=show_polling_progress,
        **kwargs
    )
    
    # Run generation and wait for completion
    service.run_and_wait(
        max_attempts=max_polling_attempts,
        delay=polling_interval
    )
    
    # Get result with metadata
    return service.get_result() 