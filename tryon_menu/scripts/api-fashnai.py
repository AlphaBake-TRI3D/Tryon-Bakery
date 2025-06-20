import asyncio
import fal_client
import base64
import requests
from PIL import Image
import os
from io import BytesIO
import glob
import json
import time


INPUT_DIR = 'inputs/5pairs-v-small'
OUTPUT_DIR = 'outputs/5pairs-v-small__fashnai-quality'

async def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    print(f"Processing folder: {folder_name}")

    # Read and encode images as base64
    def read_image_as_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    garment_path = os.path.join(folder_path, "garment.jpg")
    model_path = os.path.join(folder_path, "human.jpg")
    json_path = os.path.join(folder_path, "tryon_params.json")
    with open(json_path, 'r') as f:
        tryon_params = json.load(f)
    print(tryon_params)

    garment_type = tryon_params['garment']['garment_type']
    category = 'auto'
    if garment_type == 'top':
        category = 'tops'
    elif garment_type == 'bottom':
        category = 'bottoms'
    elif garment_type == 'full':
        category = 'one-pieces'
    else:
        category = 'accessories'

    # Get the garment image path from the tryon_params
    if not (os.path.exists(garment_path) and os.path.exists(model_path)):
        print(f"Skipping {folder_name} - missing required images")
        return

    # Convert images to base64
    garment_base64 = read_image_as_base64(garment_path)
    model_base64 = read_image_as_base64(model_path)

    handler = await fal_client.submit_async(
        "fal-ai/fashn/tryon/v1.5",
        arguments={
            "model_image": f"data:image/jpeg;base64,{model_base64}",
            "garment_image": f"data:image/jpeg;base64,{garment_base64}",
            "category": category,
            "mode": "quality",
        },
    )

    async for event in handler.iter_events(with_logs=True):
        print(event)

    result = await handler.get()
    print(f"Got result for {folder_name}")

    # Download the output image
    output_url = result['images'][0]['url']
    output_path = f"{OUTPUT_DIR}/tryons/{folder_name}.jpg"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    response = requests.get(output_url)
    with open(output_path, 'wb') as f:
        f.write(response.content)

    # Create stacked visualization
    # Load all images
    model_img = Image.open(model_path)
    garment_img = Image.open(garment_path)
    output_img = Image.open(BytesIO(response.content))

    # Resize all images to height 1024 while maintaining aspect ratio
    target_height = 1024
    
    def resize_image(img):
        ratio = target_height / img.height
        new_width = int(img.width * ratio)
        return img.resize((new_width, target_height), Image.Resampling.LANCZOS)

    model_img = resize_image(model_img)
    garment_img = resize_image(garment_img)
    output_img = resize_image(output_img)

    # Create a new image with the combined width
    total_width = model_img.width + garment_img.width + output_img.width
    stacked_img = Image.new('RGB', (total_width, target_height))

    # Paste images side by side
    x_offset = 0
    stacked_img.paste(model_img, (x_offset, 0))
    x_offset += model_img.width
    stacked_img.paste(garment_img, (x_offset, 0))
    x_offset += garment_img.width
    stacked_img.paste(output_img, (x_offset, 0))

    # Save the stacked image
    stacked_path = f"{OUTPUT_DIR}/stacked/{folder_name}.jpg"
    os.makedirs(os.path.dirname(stacked_path), exist_ok=True)
    stacked_img.save(stacked_path)
    print(f"Saved stacked image for {folder_name}")

async def main():
    input_base = INPUT_DIR
    folders = [f for f in glob.glob(os.path.join(input_base, "*")) if os.path.isdir(f)]
    print(f"Found {len(folders)} folders to process")

    semaphore = asyncio.Semaphore(5)

    async def sem_task(folder):
        async with semaphore:
            try:
                start_time = time.time()
                await process_folder(folder)
                end_time = time.time()
                print(f"Time taken for {folder}: {end_time - start_time} seconds")
            except Exception as e:
                print(f"Error processing folder {folder}: {str(e)}")

    await asyncio.gather(*(sem_task(folder) for folder in folders))

if __name__ == "__main__":
    asyncio.run(main())