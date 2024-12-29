import sys
import os
from pathlib import Path

# Add the python/src directory to Python path
repo_root = Path(__file__).parent.parent
sys.path.append(str(repo_root / "python" / "src"))

from dotenv import load_dotenv
from tryon_tray.api.video_gen import generate_video
from tryon_tray.types.video import VideoModelVersion, VideoMode, VideoDuration
from datetime import datetime
import time

# Load environment variables from .env file
load_dotenv()

# Setup paths
script_dir = Path(__file__).parent
inputs_dir = script_dir / "inputs"
outputs_dir = script_dir / "outputs"

# Create directories if they don't exist
inputs_dir.mkdir(exist_ok=True)
outputs_dir.mkdir(exist_ok=True)

# Input image path
source_image = str(inputs_dir / "person.jpg")
output_path = str(outputs_dir / f"video_kling_{int(time.time())}.mp4")

print(f"Using source image: {source_image}")
print(f"Output will be saved to: {output_path}")

# Generate video
result = generate_video(
    source_image=source_image,
    prompt="person walking naturally, high quality, detailed",
    mode=VideoMode.STANDARD.value,  # "std" or "pro"
    duration=VideoDuration.FIVE.value,  # "5" or "10"
    show_polling_progress=True,
    auto_download=True,
    download_path=output_path,
    # Optional parameters
    negative_prompt="bad quality, blurry, distorted",
    cfg_scale=0.7,
    seed=42
)

# Print results
print("\nGeneration completed!")
print(f"Video URL: {result.video_url}")
print(f"Task ID: {result.task_id}")

if result.local_path:
    print(f"\nVideo downloaded to: {result.local_path}")

if result.timing:
    print(f"\nTiming information:")
    print(f"Time taken: {result.timing['time_taken']}") 