import logging
import traceback
from fastapi import APIRouter, HTTPException, status, Body
from typing import Dict, Any

from pydantic import BaseModel


from data.models.topology.world_model import get_topology_from_redis
from server.api.simulation.manager import SimulationManager

simulation_router = APIRouter(prefix="/simulation", tags=["Simulation"])

try:
    manager = SimulationManager.get_instance()
except Exception as e:
    print(f"CRITICAL: Failed to initialize SimulationManager: {e}")
    manager = None


class SendMessageRequest(BaseModel):
    from_node_name: str
    to_node_name: str
    message: str


@simulation_router.get("/status/", summary="Get current simulation status")
async def get_simulation_status():
    """
    Returns whether the simulation managed by the SimulationManager is currently running.
    """
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
        # First, check notebook-provided status file so the UI can unblock before manager starts
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
        if manager is None or not manager.is_running:
            # If no simulation running, use notebook status to decide whether to block the UI
            if notebook_ready:
                return {
                    "requires_student_implementation": True,
                    "has_valid_implementation": True,
                    "message": "Student implementation detected from notebook.",
                    "blocking_reason": None,
                }
            else:
                return {
                    "requires_student_implementation": True,
                    "has_valid_implementation": False,
                    "message": "VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION",
                    "blocking_reason": "No simulation running - student implementation will be required when started",
                }
        
        # Check current simulation for quantum hosts that need student implementation
        world = getattr(manager, "simulation_world", None)
        if world is None:
            return {
                "requires_student_implementation": True,
                "has_valid_implementation": bool(notebook_ready),
                "message": (
                    "Student implementation detected from notebook."
                    if notebook_ready
                    else "VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION"
                ),
                "blocking_reason": None if notebook_ready else "No world loaded",
            }
        
        # Check all quantum hosts in all zones
        student_implementation_required = False
        has_valid_implementation = True
        blocking_hosts = []
        
        for zone in getattr(world, 'zones', []) or []:
            # Zone has networks; iterate networks -> nodes
            for network in getattr(zone, 'networks', []) or []:
                for node in getattr(network, 'nodes', []) or []:
                    if hasattr(node, 'require_student_code') and node.require_student_code:
                        student_implementation_required = True
                        if not hasattr(node, 'student_code_validated') or not node.student_code_validated:
                            has_valid_implementation = False
                            blocking_hosts.append(getattr(node, 'name', 'unknown'))
        
        # If notebook indicates ready, prefer that signal to unblock UI
        if notebook_ready:
            has_valid_implementation = True
            blocking_hosts = []

        if student_implementation_required and not has_valid_implementation:
            return {
                "requires_student_implementation": True,
                "has_valid_implementation": False,
                "message": "VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION",
                "blocking_reason": f"Quantum hosts require student implementation: {', '.join(blocking_hosts)}",
                "blocking_hosts": blocking_hosts
            }
        
        return {
            "requires_student_implementation": student_implementation_required,
            "has_valid_implementation": has_valid_implementation,
            "message": "Student implementation is working correctly!" if has_valid_implementation else "",
            "blocking_reason": None
        }
        
    except Exception as e:
        print(f"Error checking student implementation status: {e}")
        # Default to requiring student implementation on error
        return {
            "requires_student_implementation": True,
            "has_valid_implementation": False,
            "message": "VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION",
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
