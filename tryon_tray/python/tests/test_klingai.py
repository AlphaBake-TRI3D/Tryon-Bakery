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

def test_klingai_basic(test_images):
    """Test basic Kling.ai functionality"""
    result = VTON(
        model_image=test_images["model"],
        garment_image=test_images["garment"],
        model_name="klingai"
    )
    
    assert "urls" in result
    assert isinstance(result["urls"], list)
    assert len(result["urls"]) > 0

def test_klingai_with_download(test_images, output_dir):
    """Test Kling.ai with auto-download"""
    result = VTON(
        model_image=test_images["model"],
        garment_image=test_images["garment"],
        model_name="klingai",
        auto_download=True,
        download_dir=output_dir
    )
    
    assert "local_paths" in result
    for path in result["local_paths"]:
        assert os.path.exists(path) 