import os
import requests
import dotenv
from pathlib import Path
import time

dotenv.load_dotenv()

VMODEL_API_KEY = os.getenv("VMODEL_API_KEY")
if not VMODEL_API_KEY:
    raise ValueError("Please set VMODEL_API_KEY environment variable")

BASE_URL = "https://developer.vmodel.ai/api/vmodel/v1/ai-virtual-try-on"
HEADERS = {
    "Authorization": VMODEL_API_KEY,
    "accept": "application/json"
}

def create_job(model_image_path: str, garment_image_path: str, clothes_type: str = "upper_body", prompt: str = ""):
    """Create a virtual try-on job"""
    files = [
        ('clothes_image', (os.path.basename(garment_image_path), open(garment_image_path, 'rb'), 'image/png')),
        ('custom_model', (os.path.basename(model_image_path), open(model_image_path, 'rb'), 'image/png'))
    ]
    
    payload = {
        'clothes_type': clothes_type,
        'prompt': prompt
    }
    
    response = requests.post(f"{BASE_URL}/create-job", headers=HEADERS, data=payload, files=files)
    response.raise_for_status()
    
    return response.json()["result"]["job_id"]

def fetch_job(job_id: str, max_attempts: int = 60, delay: int = 5):
    """Fetch the job status and results"""
    for _ in range(max_attempts):
        response = requests.get(f"{BASE_URL}/get-job/{job_id}", headers=HEADERS)
        response.raise_for_status()
        result = response.json()
        
        if result["code"] == 100000 and result["result"]["output_image_url"]:
            return result["result"]["output_image_url"]
        elif result["code"] == 300104:
            raise Exception("Image generation failed.")
        
        print(f"Status: {result['message']['en']}. Waiting {delay} seconds...")
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
        job_id = create_job(model_image, garment_image, clothes_type="upper_body", prompt="A stylish look")
        print(f"Job ID: {job_id}")
        
        # Poll for results
        print("Polling for results...")
        output_urls = fetch_job(job_id)
        
        # Download results
        for i, url in enumerate(output_urls):
            output_path = outputs_dir / f"result_vmodel_{i}.png"
            print(f"Downloading result to {output_path}")
            download_image(url, str(output_path))
            
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
