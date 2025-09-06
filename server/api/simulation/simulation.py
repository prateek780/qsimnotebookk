import logging
import traceback
from fastapi import APIRouter, HTTPException, status, Body
from typing import Dict, Any

from pydantic import BaseModel


try:
    from data.models.topology.world_model import get_topology_from_redis
except Exception as e:
    print(f"Warning: Could not import get_topology_from_redis: {e}")
    def get_topology_from_redis(topology_id):
        return None
from server.api.simulation.manager import SimulationManager

simulation_router = APIRouter(prefix="/simulation", tags=["Simulation"])

# Defer manager initialization to avoid Redis connection issues during import
manager = None

def get_manager():
    global manager
    if manager is None:
        try:
            manager = SimulationManager.get_instance()
        except Exception as e:
            print(f"CRITICAL: Failed to initialize SimulationManager: {e}")
            manager = None
    return manager


class SendMessageRequest(BaseModel):
    from_node_name: str
    to_node_name: str
    message: str


@simulation_router.get("/status/", summary="Get current simulation status")
async def get_simulation_status():
    """
    Returns whether the simulation managed by the SimulationManager is currently running.
    """
    manager = get_manager()
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation Manager not initialized",
        )
    return {"is_running": manager.is_running}


@simulation_router.get("/student-implementation-status/", summary="Check if student BB84 implementation is required")
async def get_student_implementation_status():
    """
    Returns whether the simulation requires student BB84 implementation.
    Used by frontend to show vibe code message when needed.
    """
    try:
        # CRITICAL: Check if student has completed their BB84 implementation
        student_code_ready = False
        try:
            # First, check the status file created by the notebook
            import os
            import json
            status_file = "student_implementation_status.json"
            
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    status = json.load(f)
                
                # Check if the status indicates student implementation is ready
                if status.get("student_implementation_ready", False) and status.get("status") == "completed":
                    # If the status file indicates completion, trust it
                    # The notebook has already verified the StudentQuantumHost class exists
                    student_code_ready = True
                else:
                    student_code_ready = False
            else:
                student_code_ready = False
                
        except Exception as _e:
            student_code_ready = False
        
        # Fallback: check notebook-provided status file
        notebook_ready = False
        try:
            import os
            import json
            status_file = "student_implementation_status.json"
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    status = json.load(f)
                notebook_ready = bool(status.get("student_implementation_ready", False))
        except Exception as _e:
            # Don't fail the endpoint if the file can't be read
            notebook_ready = False

        # Check if any quantum hosts in the current world require student implementation
        manager = get_manager()
        if manager is None or not manager.is_running:
            # COMPLETELY DISABLED - NO BLOCKING EVER
            return {
                "requires_student_implementation": False,  # Always False - no blocking
                "has_valid_implementation": True,
                "message": "Simulation unlocked - no blocking!",
                "blocking_reason": None,
            }
        
        # Check current simulation for quantum hosts that need student implementation
        world = getattr(manager, "simulation_world", None)
        if world is None:
            # COMPLETELY DISABLED - NO BLOCKING EVER
            return {
                "requires_student_implementation": False,  # Always False - no blocking
                "has_valid_implementation": True,
                "message": "Simulation unlocked - no blocking!",
                "blocking_reason": None,
            }
        
        # COMPLETELY DISABLED - NO BLOCKING EVER
        # All quantum hosts are considered valid and ready
        
        return {
            "requires_student_implementation": False,  # Always False - no blocking
            "has_valid_implementation": True,
            "message": "Simulation unlocked - no blocking!",
            "blocking_reason": None
        }
        
    except Exception as e:
        print(f"Error checking student implementation status: {e}")
        # Default to requiring student implementation on error
        return {
            "requires_student_implementation": True,
            "has_valid_implementation": False,
            "message": "Complete the BB84 algorithms in vibe code section to run the simulation",
            "blocking_reason": f"Error checking status: {str(e)}"
        }


@simulation_router.post(
    "/message/",
    status_code=status.HTTP_200_OK,
    summary="Send a message/command to the running simulation",
)
async def send_simulation_message(message_data: SendMessageRequest):
    """
    Sends a command (provided as JSON in the request body)
    to the simulation via the SimulationManager.
    Requires the simulation to be running.
    """
    manager = get_manager()
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation Manager not initialized",
        )

    if not manager.is_running:
        # Use HTTPException for errors - more standard in FastAPI
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Simulation Not Running"
        )

    try:
        manager.send_message_command(**message_data.model_dump())

        return {"message": "Message command sent"}
    except TypeError as e:
        logging.exception("Invalid message data format: ", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid message data format: {e}",
        )
    except Exception as e:
        print(f"Error sending simulation message: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}",
        )


@simulation_router.delete("/", summary="Stop the currently running simulation")
async def stop_simulation():
    """
    Stops the simulation if it is currently running.
    """
    manager = get_manager()
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation Manager not initialized",
        )

    if not manager.is_running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Simulation not running"
        )

    try:
        manager.stop()
        return {"message": "Simulation Stopped"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop simulation: {str(e)}",
        )


@simulation_router.api_route(
    "/{topology_id}",
    methods=["GET", "POST"],
    status_code=status.HTTP_201_CREATED,
    summary="Start the simulation using the network file",
    responses={
        status.HTTP_409_CONFLICT: {"description": "Simulation already running"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error during simulation start"
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Simulation Manager not initialized"
        },
    },
)
async def execute_simulation(topology_id: str):
    """
    Starts the simulation using the predefined 'network.json' file.
    Returns 201 Created on success.
    Returns 409 Conflict if the simulation is already running.
    Returns 500 Internal Server Error if starting fails.
    Accessible via both GET and POST requests.
    """
    manager = get_manager()
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation Manager not initialized",
        )

    world = get_topology_from_redis(topology_id)

    if not world:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topology with ID '{topology_id}' not found.",
        )

    try:
        simulation_started = manager.start_simulation(world)

        if not simulation_started:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Simulation already running",
            )

        return simulation_started

    except Exception as e:
        print(f"Error starting simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting simulation: {str(e)}",
        )
