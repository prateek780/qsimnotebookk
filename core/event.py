import time
from typing import TYPE_CHECKING

from core.enums import SimulationEventType
try:
    from data.models.simulation.log_model import LogLevel
except Exception:
    # Fallback when Redis models are unavailable (e.g., running notebook without redis_om)
    from enum import Enum

    class LogLevel(str, Enum):
        DEBUG = "debug"
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        CRITICAL = "critical"
from utils.encoding import transform_val

if TYPE_CHECKING:
    from core.s_object import Sobject


class Event:
    def __init__(self, event_type: SimulationEventType, node: 'Sobject', **kwargs):
        self.event_type = event_type
        self.node = node
        self.timestamp = time.time()
        self.data = kwargs
        self.log_level = kwargs.get("log_level", LogLevel.INFO)

    def to_dict(self):
        return {
            "event_type": self.event_type.value,
            "node": self.node.name,
            "timestamp": self.timestamp,
            "data": {k: transform_val(v) for k, v in self.data.items()},
            "log_level": self.log_level.value if hasattr(self.log_level, 'value') else str(self.log_level),
        }
