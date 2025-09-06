import asyncio
from datetime import datetime
from pprint import pprint
import threading
import time
from typing import List, Optional, Dict, Any
import traceback
import json
import os

from ai_agent.src.agents.base.enums import AgentTaskType
from ai_agent.src.agents.log_summarization.structures import RealtimeLogSummaryInput
from ai_agent.src.consts.agent_type import AgentType
from ai_agent.src.orchestration.coordinator import Coordinator
from config.config import get_config
from core.base_classes import World
from core.enums import SimulationEventType
from core.event import Event
from data.embedding.embedding_util import EmbeddingUtil
from data.models.simulation.log_model import LogEntryModel, add_log_entry
from data.models.simulation.simulation_model import (
    SimulationModal,
    SimulationStatus,
    save_simulation,
    update_simulation_status,
)
from data.models.topology.world_model import WorldModal
from json_parser import simulate_from_json
from server.socket_server.socket_server import ConnectionManager
from tasks import summarize_logs_task
import importlib
import json
import os


class SimulationManager:
    _instance: Optional["SimulationManager"] = None
    simulation_world: World = None
    logs_to_summarize :List[LogEntryModel]= []
    last_summarized_on: int = None
    agent_coordinator = Coordinator()
    current_log_summary: List[str] = []
    socket_conn: ConnectionManager = None
    config = get_config()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SimulationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.is_running = False
        self.socket_conn = ConnectionManager()
        self.current_simulation = None
        self.simulation_data: SimulationModal = None
        self.main_event_loop = None
        self.embedding_util = EmbeddingUtil()
        self.embedding_enabled = True  # Start with embedding enabled
        
        # Initialize log file saving
        self.log_file_path = None
        self.log_file_handle = None
        self.simulation_logs = []  # Store all logs for final file output

    @classmethod
    def get_instance(cls) -> "SimulationManager":
        """Get or create the singleton instance"""
        if cls._instance is None:
            return cls()
        return cls._instance

    @classmethod
    def destroy_instance(cls) -> None:
        """Reset the singleton instance"""
        if cls._instance is not None:
            cls._instance.stop()
            cls._instance = None

    def start_simulation(self, network: WorldModal) -> bool:
        if self.is_running:
            return False

        try:
            self.is_running = True
            self.simulation_data = SimulationModal(
                world_id=network.pk,
                name=network.name,
                status=SimulationStatus.PENDING,
                start_time=datetime.now(),
                end_time=None,
                configuration=network,
                metrics=None,
            )
            self.save_simulation = save_simulation(self.simulation_data)
            
            # Initialize log file for this simulation
            self._initialize_log_file(network.name)
            try:
                self.main_event_loop = asyncio.get_running_loop()
                print(f"Captured main event loop: {self.main_event_loop}")
            except RuntimeError:
                print(
                    "CRITICAL WARNING: Could not get running loop when starting simulation. "
                    "Ensure start_simulation is called from an async context (e.g., await manager.start_simulation). "
                    "Event broadcasting will likely fail."
                )
                self.main_event_loop = None  # Ensure it's None if failed
            # Start the simulation process
            self._run_simulation(network)

            return self.simulation_data

        except Exception as e:
            self.emit_event(
                "simulation_error",
                {
                    "message": f"Error starting simulation: {str(e)}",
                    "traceback": traceback.format_exc(),
                },
            )
            raise

    def on_update(self, event: Event) -> None:
        self.emit_event("simulation_event", event.to_dict())
        
        # Create formatted log entry for file saving
        self._save_log_to_file(event)
        
        log_entry = add_log_entry(
            {
                "simulation_id": self.simulation_data.pk,
                "timestamp": datetime.now(),
                "level": event.log_level,
                "component": event.node.name,
                "entity_type": getattr(event.node, "type", None),
                "details": event.to_dict(),
            }
        )
        # Handle log entry safely - only if not None and Redis is available
        if log_entry is not None:
            # Try to store in Redis if available, but don't crash if it fails
            try:
                if hasattr(self, 'embedding_util') and self.embedding_util:
                    # Only try embedding if Redis is working
                    self.embedding_util.embed_and_store_log(log_entry)
            except Exception as e:
                # Silently ignore Redis errors - don't crash the simulation
                if "OutOfMemoryError" not in str(e) and "maxmemory" not in str(e):
                    print(f"⚠️ Log storage warning: {e}")
            
            # Always add to logs for potential summarization
            self.logs_to_summarize.append(log_entry)

    def _summarize_delta_logs(self) -> None:
        SUMMARIZE_EVERY_SECONDS = 2

        if (self.last_summarized_on is None or 
            time.time() - self.last_summarized_on >= SUMMARIZE_EVERY_SECONDS) and self.logs_to_summarize:
            
            logs_to_summarize = self.logs_to_summarize.copy()
            self.logs_to_summarize.clear()
            
            # Check if Redis is available for Celery
            try:
                from data.models.connection.redis import get_redis_conn
                redis_conn = get_redis_conn()
                if redis_conn is not None:
                    # Use Celery when Redis is available
                    task = summarize_logs_task.delay(
                        simulation_id=self.simulation_data.pk,
                        previous_summary=self.current_log_summary,
                        new_logs=[l.to_human_string() for l in logs_to_summarize],
                        conversation_id=self.simulation_data.pk
                    )
                    
                    # Schedule result handler to run on main event loop
                    def schedule_result_handler():
                        asyncio.create_task(self._handle_celery_result(task))
                    
                    self.main_event_loop.call_soon_threadsafe(schedule_result_handler)
                else:
                    # Run directly when Redis is not available
                    asyncio.create_task(self._run_direct_log_summarization(logs_to_summarize))
            except Exception as e:
                print(f"Error in log summarization: {e}")
                # Fallback to direct summarization
                asyncio.create_task(self._run_direct_log_summarization(logs_to_summarize))
    
    async def _run_direct_log_summarization(self, logs_to_summarize):
        """Run log summarization directly when Celery is not available"""
        try:
            from ai_agent.src.orchestration.coordinator import Coordinator
            from ai_agent.src.agents.base.enums import AgentTaskType
            from ai_agent.src.agents.log_summarization.structures import RealtimeLogSummaryInput
            
            coordinator = Coordinator()
            
            # Create input for realtime log summary
            agent_args = RealtimeLogSummaryInput(
                simulation_id=self.simulation_data.pk,
                previous_summary=self.current_log_summary,
                new_logs=[l.to_human_string() for l in logs_to_summarize],
                conversation_id=self.simulation_data.pk,
                optional_instructions=None
            )
            
            # Run the log summarization directly
            result = await coordinator._run_agent_task(AgentTaskType.REALTIME_LOG_SUMMARY, {
                'task_id': AgentTaskType.REALTIME_LOG_SUMMARY,
                'input_data': agent_args
            })
            
            if result and 'summary_text' in result:
                # Update the current log summary
                self.current_log_summary.extend(result['summary_text'])
                self.last_summarized_on = time.time()
                
                # Emit the summary to the frontend
                self.emit_event("simulation_summary", {
                    "summary_text": result['summary_text'],
                    "full_summary": self.current_log_summary
                })
                
                print(f"Generated log summary: {result['summary_text']}")
            else:
                print("No summary generated from logs")
                
        except Exception as e:
            print(f"Error in direct log summarization: {e}")
            import traceback
            traceback.print_exc()
    
    async def _handle_celery_result(self, task):
        """Handle Celery task result asynchronously"""
        try:
            # Poll for result without blocking
            while not task.ready():
                await asyncio.sleep(0.1)
            
            summary_result = task.result
            self.last_summarized_on = time.time()
            
            if summary_result is not None:
                new_summary = summary_result['summary_text']
                if len(new_summary) == 1:
                    self.current_log_summary.append(new_summary[0])
                else:
                    self.current_log_summary = new_summary
                    
                summary_result['summary_text'] = self.current_log_summary
                self.emit_event("simulation_summary", summary_result)
                
        except Exception as e:
            print(f"Error handling Celery result: {e}")

    def _run_simulation(self, topology_data: WorldModal) -> None:
        """
        Run the actual simulation process
        This would be where your simulation logic lives
        """
        try:
            import time
            from threading import Thread

            def simulation_worker():
                try:
                    self.emit_event(
                        "simulation_started", {"time": datetime.now().timestamp()}
                    )

                    # Mark as running
                    self.simulation_data.status = SimulationStatus.RUNNING
                    update_simulation_status(
                        self.simulation_data.pk, SimulationStatus.RUNNING
                    )

                    self.simulation_world = simulate_from_json(
                        topology_data.model_dump(), self.on_update
                    )

                    # Attach student implementation to hosts if provided via plugin
                    try:
                        self._attach_student_impl_to_hosts()
                    except Exception as e:
                        print(f"Warning: could not attach student implementation: {e}")

                    while self.simulation_world.is_running:
                        time.sleep(2)
                        # DISABLED: Skip log summarization to avoid Redis issues
                        pass

                    self.emit_event(
                        "simulation_completed",
                        {"results": self.simulation_data["results"]},
                    )
                    self.simulation_data.status = SimulationStatus.COMPLETED
                    update_simulation_status(
                        self.simulation_data.pk, SimulationStatus.COMPLETED
                    )
                    
                    # Save final log file when simulation completes
                    self._finalize_log_file()

                except Exception as e:
                    self._handle_error(e)
                    self.simulation_data.status = SimulationStatus.FAILED
                    update_simulation_status(
                        self.simulation_data.pk, SimulationStatus.FAILED
                    )
                    
                    # Save log file even if simulation fails
                    self._finalize_log_file()

                finally:
                    # Reset run state if this wasn't from an external stop
                    if self.is_running:
                        self.is_running = False

            # Run simulation in background
            Thread(target=simulation_worker).start()

        except Exception as e:
            self._handle_error(e)

    def send_message_command(
        self, from_node_name: str, to_node_name: str, message: str, **kwargs
    ):
        # Check if simulation world exists
        if self.simulation_world is None:
            print(f"⚠️ Simulation world not available, cannot send message from {from_node_name} to {to_node_name}")
            return
            
        from_node = to_node = None
        for network in self.simulation_world.networks:
            for node in network.nodes:
                if node.name == from_node_name:
                    from_node = node
                    continue
                if node.name == to_node_name:
                    to_node = node
                    continue

        if not (from_node and to_node):
            print(f"⚠️ Nodes not found: {from_node_name} or {to_node_name}")
            return

        try:
            from_node.send_data(message, to_node)
            print(f"✅ Message sent from {from_node_name} to {to_node_name}: {message}")
        except Exception as e:
            print(f"⚠️ Error sending message: {e}")

    def _attach_student_impl_to_hosts(self) -> None:
        """Attach student implementation plugin (if present) to InteractiveQuantumHost nodes."""
        if not self.simulation_world:
            return
        status_file = "student_implementation_status.json"
        module_name = class_name = None
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    status = json.load(f)
                module_name = status.get("student_plugin_module")
                class_name = status.get("student_plugin_class")
            except Exception:
                module_name = class_name = None

        if not module_name or not class_name:
            return

        try:
            module = importlib.import_module(module_name)
            plugin_cls = getattr(module, class_name, None)
        except Exception as e:
            print(f"Failed to import student plugin {module_name}.{class_name}: {e}")
            return

        try:
            from quantum_network.interactive_host import InteractiveQuantumHost
        except Exception as e:
            print(f"Failed to import InteractiveQuantumHost: {e}")
            return

        for network in getattr(self.simulation_world, 'networks', []) or []:
            for node in getattr(network, 'nodes', []) or []:
                if isinstance(node, InteractiveQuantumHost) and getattr(node, 'student_implementation', None) is None:
                    try:
                        node.student_implementation = plugin_cls(node)
                        node.validate_student_implementation()
                    except Exception as e:
                        print(f"Could not attach plugin to host {getattr(node, 'name', 'unknown')}: {e}")

    def stop(self) -> None:
        """Stop the running simulation"""
        if not self.is_running:
            return

        self.is_running = False

        if self.current_simulation is not None:
            # Add logic to safely stop your simulation
            # self.current_simulation.stop()
            self.current_simulation = None

        self.simulation_data.status = SimulationStatus.COMPLETED
        update_simulation_status(self.simulation_data.pk, SimulationStatus.COMPLETED)
        self.simulation_world.stop()

    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status"""
        return {
            "is_running": self.is_running,
            "progress": self.simulation_data.get("progress", 0),
            "status": self.simulation_data.get("status", "idle"),
            "results": self.simulation_data.get("results"),
            "error": self.simulation_data.get("error"),
        }

    def emit_event(self, event: str, data: Dict[str, Any]) -> None:
        """
        Emit event to connected clients via Socket using run_coroutine_threadsafe.
        This method is designed to be called safely FROM A WORKER THREAD.

        Args:
            event: Event name
            data: Event data
        """
        # Check if we have the connection manager and the main loop reference
        if not self.socket_conn:
            print(
                f"[{threading.current_thread().name}] Warning: Socket connection manager not available. Cannot emit '{event}'."
            )
            return
        if not self.main_event_loop or not self.main_event_loop.is_running():
            print(
                f"[{threading.current_thread().name}] Warning: Main event loop not available or not running. Cannot emit '{event}'."
            )
            return

        try:
            if hasattr(data, "to_dict"):
                data = data.to_dict()
            
            # Ensure all data is JSON serializable
            data = self._make_json_serializable(data)
            
            # Test JSON serialization
            json.dumps(data)
        except Exception as e:
            print(
                f"[{threading.current_thread().name}] Error serializing data for event '{event}': {e}"
            )
            print(f"Data type: {type(data)}")
            pprint(data)
            return

        coro_to_run = self.socket_conn.broadcast(dict(event=event, data=data))
        future = asyncio.run_coroutine_threadsafe(coro_to_run, self.main_event_loop)

    def _make_json_serializable(self, obj):
        """Recursively convert objects to JSON serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, 'value'):  # Handle enums
            return obj.value
        elif hasattr(obj, '__class__') and 'SimulationEventType' in str(obj.__class__):
            return obj.value
        elif hasattr(obj, '__class__') and 'SimulationEventType' in str(obj.__class__.__name__):
            return obj.value
        elif hasattr(obj, '__class__') and 'SimulationEventType' in str(type(obj)):
            return obj.value
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)

    def _handle_error(self, error: Exception) -> None:
        """
        Handle simulation errors

        Args:
            error: The exception that occurred
        """
        error_info = {"message": str(error), "traceback": traceback.format_exc()}

        self.simulation_data.status = "error"
        self.is_running = False

        self.emit_event("simulation_error", error_info)

        raise error

    def _on_progress_update(self, progress: int, message: str) -> None:
        """
        Handle progress updates from the simulation

        Args:
            progress: Progress percentage (0-100)
            message: Progress message
        """
        self.simulation_data["progress"] = progress
        self.emit_event(
            "simulation_progress", {"progress": progress, "message": message}
        )

    def _initialize_log_file(self, simulation_name: str) -> None:
        """Initialize log file for the simulation"""
        try:
            # Create logs directory if it doesn't exist
            logs_dir = "simulation_logs"
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # Create timestamped log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in simulation_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            self.log_file_path = os.path.join(logs_dir, f"simulation_log_{safe_name}_{timestamp}.txt")
            
            # Initialize log file with header
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"QUANTUM NETWORK SIMULATION LOG\n")
                f.write(f"Simulation: {simulation_name}\n")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
            
            print(f"📝 Log file initialized: {self.log_file_path}")
            
        except Exception as e:
            print(f"⚠️ Error initializing log file: {e}")
            self.log_file_path = None

    def _save_log_to_file(self, event: Event) -> None:
        """Save individual log entry to file"""
        if not self.log_file_path:
            return
            
        try:
            # Format the log entry
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # Include milliseconds
            event_type = str(event.event_type)
            node_name = event.node.name if hasattr(event.node, 'name') else 'Unknown'
            
            # Extract message from event data
            message = "No message"
            if hasattr(event, 'data') and event.data:
                if isinstance(event.data, dict):
                    message = event.data.get('message', str(event.data))
                else:
                    message = str(event.data)
            
            # Create log line
            log_line = f"[{timestamp}] {event_type} | {node_name} | {message}\n"
            
            # Append to file immediately
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_line)
                
            # Also store in memory for final summary
            self.simulation_logs.append({
                'timestamp': timestamp,
                'event_type': event_type,
                'node_name': node_name,
                'message': message,
                'full_data': event.to_dict() if hasattr(event, 'to_dict') else str(event)
            })
            
        except Exception as e:
            print(f"⚠️ Error saving log to file: {e}")

    def _finalize_log_file(self) -> None:
        """Finalize log file with summary and statistics"""
        if not self.log_file_path:
            return
            
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write("SIMULATION SUMMARY\n")
                f.write("=" * 80 + "\n")
                f.write(f"Total log entries: {len(self.simulation_logs)}\n")
                f.write(f"Simulation ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Count events by type
                event_counts = {}
                for log in self.simulation_logs:
                    event_type = log['event_type']
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                f.write("\nEvent Summary:\n")
                for event_type, count in sorted(event_counts.items()):
                    f.write(f"  {event_type}: {count}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("END OF SIMULATION LOG\n")
                f.write("=" * 80 + "\n")
            
            print(f"📝 Simulation log saved to: {self.log_file_path}")
            print(f"📊 Total log entries: {len(self.simulation_logs)}")
            
        except Exception as e:
            print(f"⚠️ Error finalizing log file: {e}")
