from .services.factory import get_vton_service
from .utils.file_io import download_image
from pathlib import Path

def VTON(
    model_image: str,
    garment_image: str,
    model_name: str = "fashnai",
    auto_download: bool = False,
    download_dir: str = "outputs",
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
        download_dir: Directory for downloaded images
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
        output_dir = Path(download_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        local_paths = []
        for i, url in enumerate(result_urls):
            output_path = output_dir / f"{model_name}_result_{i}.png"
            download_image(url, str(output_path))
            local_paths.append(str(output_path))
            
        result["local_paths"] = local_paths
    
    return result 