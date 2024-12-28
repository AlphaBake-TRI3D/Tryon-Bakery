import os
import time
import requests
import base64
from pathlib import Path
import dotenv

dotenv.load_dotenv()

FASHNAI_API_KEY = os.getenv("FASHNAI_API_KEY")
if not FASHNAI_API_KEY:
    raise ValueError("Please set FASHNAI_API_KEY environment variable")

BASE_URL = "https://api.fashn.ai/v1"
HEADERS = {
    "Authorization": f"Bearer {FASHNAI_API_KEY}",
    "Content-Type": "application/json"
}

def image_to_base64(image_path: str) -> str:
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_string}"

def run_tryon(
    model_image_path: str, 
    garment_image_path: str, 
    category: str = "tops",
    mode: str = "quality",
    nsfw_filter: bool = True,
    cover_feet: bool = False,
    adjust_hands: bool = False,
    restore_background: bool = False,
    restore_clothes: bool = False,
    garment_photo_type: str = "auto",
    long_top: bool = False,
    seed: int = 42,
    num_samples: int = 1
):
    """Initialize the try-on process with all available options
    
    Args:
        model_image_path: Path to the model/person image
        garment_image_path: Path to the garment image
        category: Type of garment ("tops", "bottoms", "one-pieces")
        mode: Processing mode ("performance", "balanced", "quality")
        nsfw_filter: Run NSFW content filter on inputs
        cover_feet: Allow long garments to cover the feet/shoes
        adjust_hands: Change the appearance of the model’s hands
        restore_background: Preserve the original background
        restore_clothes: Preserve the appearance of clothes that weren’t swapped
        garment_photo_type: Type of garment photo ("auto", "flat-lay", "model")
        long_top: Adjust parameters for long tops
        seed: Set random operations to a fixed state
        num_samples: Number of images to generate
    
    Raises:
        ValueError: If category, mode, or garment_photo_type have invalid values
    """
    
    # Validate category
    VALID_CATEGORIES = {"tops", "bottoms", "one-pieces"}
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}")
    
    # Validate mode
    VALID_MODES = {"performance", "balanced", "quality"}
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode. Must be one of: {', '.join(VALID_MODES)}")
    
    # Validate garment_photo_type
    VALID_GARMENT_PHOTO_TYPES = {"auto", "flat-lay", "model"}
    if garment_photo_type not in VALID_GARMENT_PHOTO_TYPES:
        raise ValueError(f"Invalid garment_photo_type. Must be one of: {', '.join(VALID_GARMENT_PHOTO_TYPES)}")
    
    # Ensure input files exist
    if not os.path.exists(model_image_path):
        raise FileNotFoundError(f"Model image not found: {model_image_path}")
    if not os.path.exists(garment_image_path):
        raise FileNotFoundError(f"Garment image not found: {garment_image_path}")

    # Convert images to base64
    model_base64 = image_to_base64(model_image_path)
    garment_base64 = image_to_base64(garment_image_path)

    # Prepare request payload with all options
    payload = {
        "model_image": model_base64,
        "garment_image": garment_base64,
        "category": category,
        "mode": mode,
        "nsfw_filter": nsfw_filter,
        "cover_feet": cover_feet,
        "adjust_hands": adjust_hands,
        "restore_background": restore_background,
        "restore_clothes": restore_clothes,
        "garment_photo_type": garment_photo_type,
        "long_top": long_top,
        "seed": seed,
        "num_samples": num_samples
    }

    # Make the API call
    response = requests.post(f"{BASE_URL}/run", headers=HEADERS, json=payload)
    response.raise_for_status()
    
    return response.json()["id"]

def poll_status(prediction_id: str, max_attempts: int = 60, delay: int = 5):
    """Poll the status endpoint until completion or failure"""
    
    for _ in range(max_attempts):
        response = requests.get(
            f"{BASE_URL}/status/{prediction_id}",
            headers=HEADERS
        )
        response.raise_for_status()
        result = response.json()
        
        if result["status"] == "completed":
            return result["output"]
        elif result["status"] == "failed":
            raise Exception(f"Prediction failed: {result['error']}")
        
        print(f"Status: {result['status']}. Waiting {delay} seconds...")
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
        prediction_id = run_tryon(model_image, garment_image, category="tops", mode="quality", adjust_hands=True)
        print(f"Prediction ID: {prediction_id}")
        
        # Poll for results
        print("Polling for results...")
        output_urls = poll_status(prediction_id)
        
        # Download results
        for i, url in enumerate(output_urls):
            output_path = outputs_dir / f"result_adjust_hands_{i}.png"
            print(f"Downloading result to {output_path}")
            download_image(url, str(output_path))
            
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
