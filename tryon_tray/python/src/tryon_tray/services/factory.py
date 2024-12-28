from .fashnai import FashnaiVTON
from .klingai import KlingaiVTON
from .replicate import ReplicateVTON

def get_vton_service(model_name, **kwargs):
    """Factory function to get the appropriate VTON service"""
    model_name = model_name.lower()
    
    if model_name == "fashnai":
        return FashnaiVTON(**kwargs)
    elif model_name == "klingai":
        return KlingaiVTON(**kwargs)
    elif model_name == "replicate":
        return ReplicateVTON(**kwargs)
    else:
        raise ValueError(f"Unknown VTON model_name: {model_name}") 