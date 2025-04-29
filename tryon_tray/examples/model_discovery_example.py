"""Example script for discovering models and their parameters."""

import sys
import os
from pathlib import Path

# Add the python/src directory to Python path
repo_root = Path(__file__).parent.parent
sys.path.append(str(repo_root / "python" / "src"))

from pprint import pprint
from tryon_tray import get_available_models, get_model_params, get_model_sample_config

def main():
    # Get all available models
    print("\n=== Available Models ===")
    all_models = get_available_models()
    print(all_models)
    
    # Get virtual try-on models
    print("\n=== Virtual Try-on Models ===")
    vton_models = get_available_models(category="vton")
    print(vton_models)
    
    # Get video models
    print("\n=== Video Models ===")
    video_models = get_available_models(category="video")
    print(video_models)
    
    # Get parameters for each model
    print("\n=== Model Parameters ===")
    for model in all_models:
        print(f"\n{model.upper()} Parameters:")
        params = get_model_params(model)
        pprint(params)
    
    # Get sample configurations
    print("\n=== Sample Configurations ===")
    for model in all_models:
        print(f"\n{model.upper()} Sample Config:")
        config = get_model_sample_config(model)
        pprint(config)
    
    # Example usage with configuration
    print("\n=== How to Use Sample Config ===")
    print("""
from tryon_tray import VTON, get_model_sample_config

# Get a sample configuration
config = get_model_sample_config("alphabake")

# You can modify specific parameters if needed
config["mode"] = "quality"
config["download_path"] = "custom_output.png"

# Use the config with VTON
result = VTON(model_name="alphabake", **config)
    """)

if __name__ == "__main__":
    main() 