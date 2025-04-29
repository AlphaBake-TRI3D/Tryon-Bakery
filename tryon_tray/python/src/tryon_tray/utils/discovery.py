"""Utility functions for discovering models and parameters."""

from typing import Dict, List, Any, Union

# Define model categories
VTON_MODELS = ["fashnai", "klingai", "replicate", "alphabake"]
VIDEO_MODELS = ["klingai_video"]

# Common parameters across all models
COMMON_PARAMS = {
    "model_image": "Path to the person/model image",
    "garment_image": "Path to the garment image",
    "auto_download": "Boolean to automatically download results (default: False)",
    "download_path": "Path to save downloaded images",
    "show_polling_progress": "Boolean to show progress during generation (default: False)",
}

# Model-specific parameters
MODEL_PARAMS = {
    "fashnai": {
        "category": "Garment category ('tops', 'dresses', etc)",
        "mode": "Generation mode ('quality' or 'speed')",
        "adjust_hands": "Boolean to adjust hand positions (default: False)",
        "restore_background": "Boolean to preserve original background (default: False)",
        "nsfw_filter": "Boolean to filter NSFW content (default: True)",
    },
    "klingai": {
        "category": "Garment category ('upper_body', 'lower_body', 'dress')",
        "source_cloth_preserve": "Boolean to preserve source cloth (default: False)",
        "front_view_image": "Boolean to ensure front view (default: True)",
    },
    "replicate": {
        "category": "Garment category ('top', 'bottom', 'dress')",
        "preserve_source_pose": "Boolean to preserve original pose (default: True)",
    },
    "alphabake": {
        "mode": "Generation mode ('fast', 'balanced', 'quality')",
        "garment_name": "Name for the garment (optional)",
        "tryon_name": "Name for the try-on result (optional)",
    },
    "klingai_video": {
        "start": "Start frame index",
        "end": "End frame index",
        "category": "Garment category ('upper_body', 'lower_body', 'dress')",
        "fps": "Frames per second for output video",
    }
}

def get_available_models(category: str = "all") -> List[str]:
    """Get a list of available model names in alphabetical order.
    
    Args:
        category: Filter by category ('vton', 'video', or 'all')
        
    Returns:
        List of model names in alphabetical order
    """
    if category.lower() == "vton":
        return sorted(VTON_MODELS)
    elif category.lower() == "video":
        return sorted(VIDEO_MODELS)
    else:
        return sorted(VTON_MODELS + VIDEO_MODELS)

def get_model_params(model_name: str) -> Dict[str, str]:
    """Get parameters for a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary of parameter names and descriptions
    """
    if model_name not in get_available_models():
        raise ValueError(f"Unknown model name: {model_name}. Available models: {get_available_models()}")
    
    # Combine common params with model-specific params
    params = COMMON_PARAMS.copy()
    if model_name in MODEL_PARAMS:
        params.update(MODEL_PARAMS[model_name])
    
    return params

def get_model_sample_config(model_name: str) -> Dict[str, Any]:
    """Get a sample configuration for a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary with sample parameter values
    """
    # Base configuration with default values
    config = {
        "model_image": "inputs/person.jpg",
        "garment_image": "inputs/garment.jpeg",
        "auto_download": True,
        "download_path": f"outputs/result_{model_name}.jpg",
        "show_polling_progress": True,
    }
    
    # Add model-specific sample values
    if model_name == "fashnai":
        config.update({
            "category": "tops",
            "mode": "quality",
            "adjust_hands": False,
            "restore_background": False,
        })
    elif model_name == "klingai":
        config.update({
            "category": "upper_body",
            "source_cloth_preserve": False,
            "front_view_image": True,
        })
    elif model_name == "replicate":
        config.update({
            "category": "top",
            "preserve_source_pose": True,
        })
    elif model_name == "alphabake":
        config.update({
            "mode": "balanced",
            "garment_name": "garment-example",
            "tryon_name": "tryon-example",
        })
    elif model_name == "klingai_video":
        config.update({
            "start": 0,
            "end": 30,
            "category": "upper_body",
            "fps": 30,
            "download_path": f"outputs/result_{model_name}.mp4",
        })
    
    return config 