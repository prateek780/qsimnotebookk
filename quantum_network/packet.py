from classical_network.packet import ClassicDataPacket
from core.enums import SimulationEventType


class QKDTransmissionPacket(ClassicDataPacket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.qkd_type = kwargs.get('qkd_type', 'control')  # control, data, key
        
    def to_dict(self):
        """Convert packet to dictionary for logging."""
        base_dict = super().to_dict()
        base_dict.update({
            'qkd_type': self.qkd_type,
            'event_type': SimulationEventType.QKD_MESSAGE,
            'message_type': self.data.get('type') if isinstance(self.data, dict) else None
        })
        return base_dict