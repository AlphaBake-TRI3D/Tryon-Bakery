from .services.factory import get_vton_service
from .utils.file_io import download_image
from pathlib import Path

def VTON(
    model_image: str,
    garment_image: str,
    model_name: str = "fashnai",
    auto_download: bool = False,
    download_path: str = "outputs/result.jpg",
    max_polling_attempts: int = 60,
    polling_interval: int = 5,
    show_polling_progress: bool = False,
    **kwargs
) -> dict:
    """
    High-level API for Virtual Try-On
    
    Args:
        model_image: Path or URL to person image
        garment_image: Path or URL to garment image
        model_name: Service to use ("fashnai", "klingai", "replicate")
        auto_download: If True, download result images locally
        download_path: Path for downloaded images (can be relative or absolute)
        max_polling_attempts: Maximum number of polling attempts (default: 60)
        polling_interval: Time between polling attempts in seconds (default: 5)
        show_polling_progress: If True, print polling progress information
        **kwargs: Additional parameters passed to the service
    
    Returns:
        dict with keys:
            - urls: List of result image URLs
            - local_paths: List of local file paths (if auto_download=True)
            - timing: Dict with start_time, end_time, and time_taken
    """
    kwargs["show_polling_progress"] = show_polling_progress
    service = get_vton_service(
        model_name=model_name,
        model_image=model_image,
        garment_image=garment_image,
        **kwargs
    )

    result_urls = service.run_and_wait(
        max_attempts=max_polling_attempts,
        delay=polling_interval
    )
    
    # Create result dictionary with timing information
    result = {
        "urls": result_urls,
        "timing": {
            "start_time": service.start_time,
            "end_time": service.end_time,
            "time_taken": service.time_taken
        }
    }
    
    if auto_download and isinstance(result_urls, list):
        # Handle both relative and absolute paths
        output_path = Path(download_path)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
            
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        local_paths = []
        for i, url in enumerate(result_urls):
            # For single result, use the exact path. For multiple results, add index suffix
            if len(result_urls) == 1:
                file_path = output_path
            else:
                # Insert index before file extension
                stem = output_path.stem
                suffix = output_path.suffix
                file_path = output_path.parent / f"{stem}_{i}{suffix}"
                
            download_image(url, str(file_path))
            local_paths.append(str(file_path))
            
        result["local_paths"] = local_paths
    
    return result 