import os
import time
import requests
import base64
import jwt
from pathlib import Path
import dotenv
from enum import Enum
from typing import Optional

dotenv.load_dotenv()

class ModelVersion(Enum):
    V1 = "kling-v1"
    V1_5 = "kling-v1-5"

class Mode(Enum):
    STANDARD = "std"
    PROFESSIONAL = "pro"

class Duration(Enum):
    FIVE = "5"
    TEN = "10"

KLINGAI_ACCESS_ID = os.getenv("KLINGAI_ACCESS_ID")
KLINGAI_API_KEY = os.getenv("KLINGAI_API_KEY")
if not KLINGAI_ACCESS_ID or not KLINGAI_API_KEY:
    raise ValueError("Please set KLINGAI_ACCESS_ID and KLINGAI_API_KEY environment variables")

BASE_URL = "https://api.klingai.com/v1"
HEADERS = {
    "Content-Type": "application/json"
}

class KlingAPIError(Exception):
    """Custom exception for Kling AI errors"""
    def __init__(self, status_code, service_code, message):
        self.status_code = status_code
        self.service_code = service_code
        self.message = message
        super().__init__(f"HTTP {status_code}, Service Code {service_code}: {message}")

def handle_api_error(response):
    """Handle API errors and extract service code and message"""
    try:
        error_data = response.json()
        service_code = error_data.get("code", "Unknown")
        message = error_data.get("message", response.text)
        print("Full error response:", error_data)  # Debug print
    except:
        service_code = "Unknown"
        message = response.text
        print("Raw error response:", response.text)  # Debug print
    
    raise KlingAPIError(response.status_code, service_code, message)

def encode_jwt_token(access_id, api_key):
    """Generate JWT token for authentication"""
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": access_id,
        "exp": int(time.time()) + 1800,  # 30 minutes expiry
        "nbf": int(time.time()) - 5
    }
    token = jwt.encode(payload, api_key, headers=headers)
    return token

def image_to_base64(image_path: str) -> str:
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

def validate_parameters(
    model_version: str,
    mode: str,
    duration: str,
) -> tuple[ModelVersion, Mode, Duration]:
    """Validate input parameters against allowed values"""
    
    # Validate model version
    try:
        model = ModelVersion(model_version)
    except ValueError:
        raise ValueError(f"Invalid model_version. Must be one of: {[m.value for m in ModelVersion]}")
    
    # Validate mode
    try:
        mode_enum = Mode(mode)
    except ValueError:
        raise ValueError(f"Invalid mode. Must be one of: {[m.value for m in Mode]}")
    
    # Validate duration
    try:
        duration_enum = Duration(duration)
    except ValueError:
        raise ValueError(f"Invalid duration. Must be one of: {[d.value for d in Duration]}")
    
    return model, mode_enum, duration_enum

def create_video_task(
    source_image_path: str,
    prompt: str,
    model_version: str = ModelVersion.V1_5.value,  # Default to v1.5
    mode: str = Mode.STANDARD.value,               # Default to standard mode
    duration: str = Duration.FIVE.value,           # Default to 5 seconds
    negative_prompt: str = "",
    cfg_scale: float = 0.5,
    seed: Optional[int] = None
):
    """Create a video generation task"""
    # Validate parameters
    model, mode_enum, duration_enum = validate_parameters(model_version, mode, duration)
    
    source_base64 = image_to_base64(source_image_path)

    payload = {
        "model_name": model.value,
        "mode": mode_enum.value,
        "duration": duration_enum.value,
        "image": source_base64,
        "prompt": prompt,
        "cfg_scale": cfg_scale
    }

    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if seed is not None:
        payload["seed"] = seed

    token = encode_jwt_token(KLINGAI_ACCESS_ID, KLINGAI_API_KEY)
    HEADERS["Authorization"] = f"Bearer {token}"

    print("Request payload:", {**payload, 'image': '(base64 data omitted)'})  # Debug print without image data
    
    response = requests.post(
        f"{BASE_URL}/videos/image2video",
        headers=HEADERS, 
        json=payload
    )
    
    if not response.ok:
        handle_api_error(response)
    
    return response.json()["data"]["task_id"]

def poll_video_status(task_id: str, max_attempts: int = 120, delay: int = 5):
    """Poll the status endpoint until completion or failure"""
    token = encode_jwt_token(KLINGAI_ACCESS_ID, KLINGAI_API_KEY)
    HEADERS["Authorization"] = f"Bearer {token}"
    
    for _ in range(max_attempts):
        response = requests.get(
            f"{BASE_URL}/videos/image2video/{task_id}",
            headers=HEADERS
        )
        
        if not response.ok:
            handle_api_error(response)
            
        result = response.json()
        print(f"Full response: {result}")  # Debug print
        
        if result["data"]["task_status"] == "succeed":
            videos = result["data"]["task_result"]["videos"]
            if not videos:
                raise Exception("No videos in response")
            return videos[0]["url"]  # Return the first video URL
        elif result["data"]["task_status"] == "failed":
            raise Exception(f"Task failed: {result['data'].get('task_status_msg', 'Unknown error')}")
        
        print(f"Status: {result['data']['task_status']}. Waiting {delay} seconds...")
        time.sleep(delay)
    
    raise TimeoutError("Maximum polling attempts reached")

def download_video(url: str, output_path: str):
    """Download the generated video"""
    response = requests.get(url)
    if not response.ok:
        handle_api_error(response)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    inputs_dir = script_dir / "inputs"
    outputs_dir = script_dir / "outputs"
    
    # Example parameters
    source_image = str(inputs_dir / "person.jpg")
    prompt = "The person walked forward naturally, photorealistic, high quality"
    
    # Create outputs directory if it doesn't exist
    outputs_dir.mkdir(exist_ok=True)
    
    try:
        # Start the video generation process
        print(f"Initiating video generation...")
        task_id = create_video_task(
            source_image_path=source_image,
            prompt=prompt,
            # Using defaults:
            # - model_version="kling-v1-5"
            # - mode="std"
            # - duration="5"
        )
        print(f"Task ID: {task_id}")
        
        # Poll for results
        print("Polling for results (this may take several minutes)...")
        video_url = poll_video_status(task_id)
        
        # Download result
        output_path = outputs_dir / f"result_kling_video_{int(time.time())}.mp4"
        print(f"Downloading video to {output_path}")
        download_video(video_url, str(output_path))
            
        print("Process completed successfully!")
        print(f"Video saved to: {output_path}")
        
    except KlingAPIError as e:
        print(f"Kling API Error:")
        print(f"  HTTP Status: {e.status_code}")
        print(f"  Service Code: {e.service_code}")
        print(f"  Message: {e.message}")
    except ValueError as e:
        print(f"Validation Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 