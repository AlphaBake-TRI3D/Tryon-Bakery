"""Configuration utilities."""

import os
import dotenv
from typing import Tuple

def load_config() -> None:
    """Load environment variables from .env file."""
    dotenv.load_dotenv()

def get_env_or_raise(key: str) -> str:
    """Get environment variable or raise error."""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing environment variable: {key}")
    return value

def get_klingai_credentials() -> Tuple[str, str]:
    """Get Kling.ai credentials from environment."""
    access_id = get_env_or_raise("KLINGAI_ACCESS_ID")
    api_key = get_env_or_raise("KLINGAI_API_KEY")
    return access_id, api_key

def get_fashnai_credentials() -> str:
    """Get Fashn.ai API key from environment."""
    return get_env_or_raise("FASHNAI_API_KEY")

def get_replicate_credentials() -> str:
    """Get Replicate API token from environment."""
    return get_env_or_raise("REPLICATE_API_TOKEN")

def get_replicate_api_token() -> str:
    """Get Replicate API token from environment (alias for consistency)."""
    return get_replicate_credentials()

def get_vmodel_api_token() -> str:
    """Get VModel API token from environment variables."""
    return get_env_or_raise("VMODEL_API_KEY") 