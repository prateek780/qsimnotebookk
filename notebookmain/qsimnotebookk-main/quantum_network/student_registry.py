"""
Student Implementation Registry
==============================

This module provides a registry for storing and retrieving student BB84 implementations.
Students can register their implementations here for automatic discovery by the simulation.
"""

from typing import Dict, Any, Optional

# Global registry for student implementations
REGISTRY: Dict[str, Any] = {}

def register_student_implementation(name: str, implementation: Any) -> bool:
    """
    Register a student implementation in the global registry.
    
    Args:
        name: The name/identifier for the implementation (e.g., "alice", "bob")
        implementation: The student implementation object
        
    Returns:
        True if registration was successful
    """
    try:
        REGISTRY[name.lower()] = implementation
        print(f"✅ Student implementation '{name}' registered successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to register student implementation '{name}': {e}")
        return False

def get_student_implementation(name: str) -> Optional[Any]:
    """
    Get a student implementation from the registry.
    
    Args:
        name: The name/identifier for the implementation
        
    Returns:
        The implementation object if found, None otherwise
    """
    return REGISTRY.get(name.lower())

def clear_registry():
    """Clear all registered student implementations."""
    REGISTRY.clear()
    print("🧹 Student implementation registry cleared")

def list_registered_implementations() -> Dict[str, str]:
    """
    List all registered implementations.
    
    Returns:
        Dictionary mapping names to implementation class names
    """
    return {name: type(impl).__name__ for name, impl in REGISTRY.items()}
