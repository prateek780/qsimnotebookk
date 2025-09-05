"""File-based storage for topologies when Redis is not available"""
import json
import os
from typing import List, Optional, Dict, Any

STORAGE_FILE = "topologies.json"

def save_topology_to_file(world) -> bool:
    """Save topology to file"""
    try:
        # Load existing topologies
        topologies = load_all_topologies_from_file()
        
        # Add or update the topology
        world_dict = world.model_dump()
        world_dict['pk'] = world.pk()
        
        # Check if topology already exists
        existing_index = None
        for i, existing in enumerate(topologies):
            if existing.get('pk') == world_dict['pk']:
                existing_index = i
                break
        
        if existing_index is not None:
            topologies[existing_index] = world_dict
        else:
            topologies.append(world_dict)
        
        # Save to file
        with open(STORAGE_FILE, 'w') as f:
            json.dump(topologies, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving topology to file: {e}")
        return False

def load_all_topologies_from_file(temporary_world=False, owner=None) -> List[Dict[str, Any]]:
    """Load all topologies from file"""
    try:
        if not os.path.exists(STORAGE_FILE):
            return []
        
        with open(STORAGE_FILE, 'r') as f:
            topologies = json.load(f)
        
        # Filter by temporary_world and owner
        filtered_topologies = []
        for topology in topologies:
            if topology.get('temporary_world', False) == temporary_world:
                if owner is None or topology.get('owner') == owner:
                    filtered_topologies.append(topology)
        
        return filtered_topologies
    except Exception as e:
        print(f"Error loading topologies from file: {e}")
        return []

def get_topology_from_file(topology_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific topology from file"""
    try:
        topologies = load_all_topologies_from_file()
        for topology in topologies:
            if topology.get('pk') == topology_id:
                return topology
        return None
    except Exception as e:
        print(f"Error getting topology from file: {e}")
        return None

def delete_topology_from_file(primary_key: str) -> bool:
    """Delete topology from file"""
    try:
        topologies = load_all_topologies_from_file()
        
        # Find and remove the topology
        updated_topologies = []
        for topology in topologies:
            if topology.get('pk') != primary_key:
                updated_topologies.append(topology)
        
        # Save updated list
        with open(STORAGE_FILE, 'w') as f:
            json.dump(updated_topologies, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error deleting topology from file: {e}")
        return False
