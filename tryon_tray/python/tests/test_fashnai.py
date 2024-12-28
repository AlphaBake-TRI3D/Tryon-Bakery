import os
import pytest
from pathlib import Path
from tryon_tray.vton_api import VTON

@pytest.fixture
def test_images():
    test_dir = Path(__file__).parent / "inputs"
    return {
        "model": str(test_dir / "person.jpg"),
        "garment": str(test_dir / "garment.jpeg")
    }

@pytest.fixture
def output_dir():
    return str(Path(__file__).parent / "test_outputs")

def test_fashnai_basic(test_images):
    """Test basic Fashn.ai functionality without downloading"""
    result = VTON(
        model_image=test_images["model"],
        garment_image=test_images["garment"],
        model_name="fashnai"
    )
    
    assert "urls" in result
    assert isinstance(result["urls"], list)
    assert len(result["urls"]) > 0
    assert all(url.startswith("http") for url in result["urls"])

def test_fashnai_with_download(test_images, output_dir):
    """Test Fashn.ai with auto-download enabled"""
    result = VTON(
        model_image=test_images["model"],
        garment_image=test_images["garment"],
        model_name="fashnai",
        auto_download=True,
        download_dir=output_dir
    )
    
    assert "urls" in result
    assert "local_paths" in result
    assert len(result["urls"]) == len(result["local_paths"])
    
    # Check if files were actually downloaded
    for path in result["local_paths"]:
        assert os.path.exists(path)

def test_fashnai_with_params(test_images):
    """Test Fashn.ai with additional parameters"""
    result = VTON(
        model_image=test_images["model"],
        garment_image=test_images["garment"],
        model_name="fashnai",
        category="tops",
        mode="quality",
        adjust_hands=True
    )
    
    assert "urls" in result
    assert isinstance(result["urls"], list) 