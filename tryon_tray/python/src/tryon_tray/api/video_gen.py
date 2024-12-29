from typing import Optional, Dict, Any
from ..types.video import VideoGenParams, VideoGenResponse, VideoModelVersion, VideoMode, VideoDuration
from ..services.factory import get_service, ServiceType

def generate_video(
    source_image: str,
    prompt: str,
    model_name: str = VideoModelVersion.KLING_V1_5.value,
    mode: str = VideoMode.STANDARD.value,
    duration: str = VideoDuration.FIVE.value,
    negative_prompt: str = "",
    cfg_scale: float = 0.5,
    seed: Optional[int] = None,
    auto_download: bool = False,
    download_path: Optional[str] = None,
    show_polling_progress: bool = False,
    **kwargs
) -> VideoGenResponse:
    """Generate a video from an image.
    
    Args:
        source_image: Path or URL to the source image
        prompt: Text description of desired video
        model_name: Name of the model to use (e.g., "kling-v1-5")
        mode: Generation mode ("std" or "pro")
        duration: Video duration in seconds ("5" or "10")
        negative_prompt: What to avoid in generation
        cfg_scale: Control strength of the prompt
        seed: Random seed for reproducibility
        auto_download: Whether to automatically download the video
        download_path: Path to save the downloaded video
        show_polling_progress: Whether to show polling progress
        **kwargs: Additional model-specific parameters
    
    Returns:
        VideoGenResponse containing the video URL and metadata
    """
    # Create parameters object
    params = VideoGenParams(
        source_image=source_image,
        prompt=prompt,
        model_name=model_name,
        mode=mode,
        duration=duration,
        negative_prompt=negative_prompt,
        cfg_scale=cfg_scale,
        seed=seed
    )
    
    # Get appropriate service
    service = get_service(
        service_type=ServiceType.VIDEO,
        model_name=model_name,
        source_image=source_image,
        prompt=prompt,
        mode=mode,
        duration=duration,
        negative_prompt=negative_prompt,
        cfg_scale=cfg_scale,
        seed=seed,
        auto_download=auto_download,
        download_path=download_path,
        show_polling_progress=show_polling_progress,
        **kwargs
    )
    
    # Run generation
    service.run()
    result = service.get_result()
    
    # Convert to response object
    return VideoGenResponse(
        video_url=result["video_url"],
        source_image=result["source_image"],
        prompt=result["prompt"],
        mode=result["mode"],
        duration=result["duration"],
        task_id=result.get("task_id"),
        created_at=result.get("created_at"),
        updated_at=result.get("updated_at"),
        local_path=result.get("local_path"),
        timing=result.get("timing")
    ) 