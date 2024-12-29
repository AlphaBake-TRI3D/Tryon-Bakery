"""Service factory for creating service instances."""

from enum import Enum, auto
from typing import Dict, Type, Any

class ServiceType(Enum):
    """Types of services available."""
    VTON = auto()
    VIDEO = auto()

class ServiceFactory:
    """Factory for creating service instances."""
    
    _registry: Dict[ServiceType, Dict[str, Type]] = {
        ServiceType.VTON: {},
        ServiceType.VIDEO: {}
    }
    
    @classmethod
    def register(cls, service_type: ServiceType, model_name: str, service_class: Type):
        """Register a service implementation."""
        if service_type not in cls._registry:
            cls._registry[service_type] = {}
        cls._registry[service_type][model_name] = service_class
    
    @classmethod
    def get_service(cls, service_type: ServiceType, model_name: str, **kwargs) -> Any:
        """Get a service instance by type and model name."""
        if service_type not in cls._registry:
            raise ValueError(f"Unknown service type: {service_type}")
            
        registry = cls._registry[service_type]
        if model_name not in registry:
            raise ValueError(
                f"Unknown model '{model_name}' for service type {service_type}. "
                f"Available models: {list(registry.keys())}"
            )
            
        service_class = registry[model_name]
        return service_class(**kwargs)

# Convenience functions
def get_service(service_type: ServiceType, model_name: str, **kwargs) -> Any:
    """Get a service instance."""
    return ServiceFactory.get_service(service_type, model_name, **kwargs)

def get_vton_service(model_name: str, **kwargs) -> Any:
    """Get a VTON service instance."""
    return get_service(ServiceType.VTON, model_name, **kwargs) 