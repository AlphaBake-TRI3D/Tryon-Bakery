from dotenv import load_dotenv
from tryon_tray.vton_api import VTON
from datetime import datetime
load_dotenv()
model_image = "inputs/person.jpg"
garment_image = "inputs/garment.jpeg"

#model_list = ["fashnai", "klingai","replicate"] 
result = VTON(
    model_image=model_image,
    garment_image=garment_image,
    model_name="fashnai", 
    auto_download=True,
    download_path="result.jpg",
    show_polling_progress=True,
    # Optional parameters
    category="tops",
    mode="quality",
)

print(result['timing']['time_taken'])

