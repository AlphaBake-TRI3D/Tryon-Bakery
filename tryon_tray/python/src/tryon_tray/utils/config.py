import os
from dotenv import load_dotenv

load_dotenv()

def get_fashnai_api_key():
    key = os.getenv("FASHNAI_API_KEY")
    if not key:
        raise ValueError("FASHNAI_API_KEY not set")
    return key

def get_klingai_credentials():
    access_id = os.getenv("KLINGAI_ACCESS_ID")
    api_key = os.getenv("KLINGAI_API_KEY")
    if not access_id or not api_key:
        raise ValueError("KLINGAI_ACCESS_ID and KLINGAI_API_KEY must be set")
    return access_id, api_key

def get_replicate_api_token():
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        raise ValueError("REPLICATE_API_TOKEN not set")
    return token 