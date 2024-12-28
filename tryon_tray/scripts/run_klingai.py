import os
import time
import requests
import base64
import jwt
from pathlib import Path
import dotenv

dotenv.load_dotenv()

KLINGAI_ACCESS_ID = os.getenv("KLINGAI_ACCESS_ID")
KLINGAI_API_KEY = os.getenv("KLINGAI_API_KEY")
if not KLINGAI_ACCESS_ID or not KLINGAI_API_KEY:
    raise ValueError("Please set KLINGAI_ACCESS_ID and KLINGAI_API_KEY environment variables")

BASE_URL = "https://api.klingai.com/v1/images"
HEADERS = {
    "Content-Type": "application/json"
}

def encode_jwt_token(access_id, api_key):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": access_id,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5
    }
    token = jwt.encode(payload, api_key, headers=headers)
    return token

def image_to_base64(image_path: str) -> str:
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

def create_task(model_image_path: str, garment_image_path: str):
    """Create a virtual try-on task"""
    model_base64 = image_to_base64(model_image_path)
    garment_base64 = image_to_base64(garment_image_path)

    payload = {
        "model_name": "kolors-virtual-try-on-v1",
        "human_image": model_base64,
        "cloth_image": garment_base64,
        "callback_url": ""
    }

    token = encode_jwt_token(KLINGAI_ACCESS_ID, KLINGAI_API_KEY)
    HEADERS["Authorization"] = f"Bearer {token}"

    response = requests.post(f"{BASE_URL}/kolors-virtual-try-on", headers=HEADERS, json=payload)
    response.raise_for_status()
    
    return response.json()["data"]["task_id"]

def poll_status(task_id: str, max_attempts: int = 60, delay: int = 5):
    """Poll the status endpoint until completion or failure"""
    
    for _ in range(max_attempts):
        response = requests.get(
            f"{BASE_URL}/kolors-virtual-try-on/{task_id}",
            headers=HEADERS
        )
        response.raise_for_status()
        result = response.json()
        
        if result["data"]["task_status"] == "succeed":
            return result["data"]["task_result"]["images"]
        elif result["data"]["task_status"] == "failed":
            raise Exception(f"Task failed: {result['data']['task_status_msg']}")
        
        print(f"Status: {result['data']['task_status']}. Waiting {delay} seconds...")
        time.sleep(delay)
    
    raise TimeoutError("Maximum polling attempts reached")

def download_image(url: str, output_path: str):
    """Download the generated image"""
    response = requests.get(url)
    response.raise_for_status()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    inputs_dir = script_dir / "inputs"
    outputs_dir = script_dir / "outputs"
    
    model_image = str(inputs_dir / "person.jpg")
    garment_image = str(inputs_dir / "garment.jpeg")
    
    # Create outputs directory if it doesn't exist
    outputs_dir.mkdir(exist_ok=True)
    
    try:
        # Start the try-on process
        print("Initiating try-on process...")
        task_id = create_task(model_image, garment_image)
        print(f"Task ID: {task_id}")
        
        # Poll for results
        print("Polling for results...")
        images = poll_status(task_id)
        
        # Download results
        for i, image in enumerate(images):
            output_path = outputs_dir / f"result_kling_{i}.png"
            print(f"Downloading result to {output_path}")
            download_image(image["url"], str(output_path))
            
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
