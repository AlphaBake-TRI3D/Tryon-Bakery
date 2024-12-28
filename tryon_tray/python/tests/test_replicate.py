import os
import pytest
from pathlib import Path
from tryon_tray.vton_api import VTON

@pytest.fixture
def test_images():
    test_dir = Path(__file__).parent / "test_images"
    return {
        "model": str(test_dir / "person.jpg"),
        "garment": str(test_dir / "garment.jpeg")
    }

@pytest.fixture
def output_dir():
    return str(Path(__file__).parent / "test_outputs")

def test_replicate_basic(test_images):
    """Test basic Replicate functionality"""
    result = VTON(
        model_image=test_images["model"],
        garment_image=test_images["garment"],
        model_name="replicate"
    )
    
    assert "urls" in result
    assert isinstance(result["urls"], list)

def test_replicate_with_params(test_images):
    """Test Replicate with additional parameters"""
    result = VTON(
        model_image=test_images["model"],
        garment_image=test_images["garment"],
        model_name="replicate",
        category="upper_body",
        steps=30,
        seed=42
    )
    
    assert "urls" in result 