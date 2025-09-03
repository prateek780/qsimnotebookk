from queue import Queue
import time
from typing import List, Tuple
try:
    import qutip as qt
except Exception:
    qt = None
from classical_network.connection import ClassicConnection
from classical_network.enum import PacketType
from classical_network.packet import ClassicDataPacket
from classical_network.presets.connection_presets import DEFAULT_PRESET, GIGABIT_ETHERNET
from classical_network.router import ClassicalRouter
from core.base_classes import Node, World, Zone
from core.enums import InfoEventType, NodeType, NetworkType, SimulationEventType
from core.exceptions import (
    DefaultGatewayNotFound,
    NotConnectedError,
    PairAdapterAlreadyExists,
    PairAdapterDoesNotExists,
    QuantumChannelDoesNotExists,
    UnSupportedNetworkError,
)
from core.network import Network

# from quantum_network.channel import QuantumChannel
try:
    from quantum_network.host import QuantumHost
except ImportError as e:
    print(f"Warning: Could not import QuantumHost: {e}")
    QuantumHost = None
from quantum_network.packet import QKDTransmissionPacket
from utils.mtu_fragmentation import fragment_packet
from utils.simple_encryption import simple_xor_decrypt, simple_xor_encrypt

# from quantum_network.node import QuantumNode
# from quantum_network.repeater import QuantumRepeater
# from classical_network.router import ClassicalRouter


class QuantumAdapter(Node):
    def __init__(
        self,
        address: str,
        classical_network: Network,
        quantum_network: Network,
        location: Tuple,
        paired_adapter: "QuantumAdapter",
        quantum_host: QuantumHost,
        zone=None,
        name="",
        description="",
    ):
        super().__init__(address, location, classical_network, zone, name, description)
        self.type = NodeType.QUANTUM_ADAPTER
        self.classical_network = classical_network
        self.quantum_network = quantum_network
        self.input_data_buffer = Queue()

        self.shared_key = None  # Store the shared secret key here
        self.qkd_in_progress = False  # Track if QKD is currently in progress
        self.last_qkd_time = 0  # Track when the last QKD was initiated

        self.local_quantum_host = quantum_host
        self.local_quantum_host.send_classical_data = self.send_classical_data
        self.local_quantum_host.qkd_completed_fn = self.on_qkd_established
        self.local_classical_router = ClassicalRouter(
            f"InternalQCRouter{self.name}",
            self.location,
            self.classical_network,
            self.zone,
            f"QC_Router_{self.name}",
        )
        self.local_classical_router.route_packet = self.intercept_route_packet

        self.paired_adapter = paired_adapter  # Reference to the paired adapter
        if paired_adapter:
            # TODO: Add connection config
            connection = ClassicConnection(
                self.local_classical_router,
                self.paired_adapter.local_classical_router,
                DEFAULT_PRESET,
                name="QC_Router_Connection",
            )
            self.local_classical_router.add_connection(connection)
            self.paired_adapter.local_classical_router.add_connection(connection)

        if paired_adapter and (
            not self.local_quantum_host.channel_exists(
                paired_adapter.local_quantum_host
            )
        ):
            raise QuantumChannelDoesNotExists(self)

    def add_paired_adapter(self, adapter: "QuantumAdapter"):
        if self.paired_adapter:
            raise PairAdapterAlreadyExists(self, self.paired_adapter)

        self.paired_adapter = adapter

    def on_qkd_established(self, key: List[int]):
        """Handle successful QKD completion and key establishment."""
        self.shared_key = key
        key_str = ''.join(map(str, self.shared_key))
        self.qkd_in_progress = False  # Reset QKD progress flag
        
        self.logger.info(f"QKD completed successfully at {self.name}")
        self._send_update(SimulationEventType.SHARED_KEY_GENERATED, key=key_str)
        self._send_update(
            SimulationEventType.INFO,
            data=dict(
                type="qkd_complete",
                message=f"QKD completed at {self.name}, shared key established"
            )
        )
        
        # Notify paired adapter about key establishment
        self.send_classical_data({
            "type": "key_established",
            "key": key_str,
            "time": time.time()
        })

        # Process any packets that were buffered during QKD
        self.process_buffered_packets()

    def calculate_distance(self, node1, node2):
        # Simple Euclidean distance calculation, adjust as needed for your network topology
        x1, y1 = node1.location
        x2, y2 = node2.location
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def initiate_qkd(self):
        """Initiate QKD with the paired adapter if not already in progress."""
        if not self.paired_adapter:
            self.logger.error(f"{self.name} has no paired adapter to perform QKD.")
            raise PairAdapterDoesNotExists(self)

        current_time = time.time()
        
        # Check if QKD is already in progress
        if self.qkd_in_progress:
            self.logger.info(f"QKD already in progress at {self.name}, skipping new request")
            return False
            
        # Check if we already have a shared key
        if self.shared_key is not None:
            self.logger.info(f"{self.name} already has a shared key with {self.paired_adapter.name}")
            return False
        
        # Add a small delay between QKD attempts to prevent rapid retries
        if current_time - self.last_qkd_time < 1.0:  # 1 second minimum delay
            self.logger.info(f"Too soon to start new QKD at {self.name}, waiting...")
            return False

        self.qkd_in_progress = True
        self.last_qkd_time = current_time
        
        self.logger.info(f"Initiating QKD between {self.name} and {self.paired_adapter.name}")
        self._send_update(
            SimulationEventType.INFO,
            data=dict(
                type="qkd_start",
                message=f"Starting QKD process between {self.name} and {self.paired_adapter.name}"
            )
        )
        
        self.local_quantum_host.perform_qkd()
        self._send_update(SimulationEventType.QKD_INITIALIZED, with_adapter=self.paired_adapter)
        return True

    def receive_packet(self, packet: ClassicDataPacket | QKDTransmissionPacket):
        """Handle incoming packets, both classical and QKD control messages."""
        if (
            packet.hops 
            and packet.hops[-2] == self.paired_adapter.local_classical_router
            and type(packet) == ClassicDataPacket
        ):
            # Handle encrypted classical data
            self.process_packet(packet)
        elif type(packet) == QKDTransmissionPacket:
            # Handle QKD control messages
            try:
                msg_type = packet.data.get('type', 'unknown') if isinstance(packet.data, dict) else 'unknown'
                self._send_update(
                    SimulationEventType.INFO,
                    data=dict(
                        type="qkd_control",
                        message=f"QKD control message '{msg_type}' received at {self.name}",
                        from_router=str(packet.from_address),
                        to_router=str(packet.to_address),
                    ),
                )
                
                # Process different types of QKD control messages
                if msg_type == "key_established":
                    # Key establishment completed
                    self.shared_key = [int(x) for x in packet.data.get('key', '')]
                    self._send_update(
                        SimulationEventType.INFO,
                        data=dict(
                            type="qkd_complete",
                            message=f"QKD completed successfully at {self.name}"
                        )
                    )
                    self._send_update(SimulationEventType.SHARED_KEY_RECEIVED, key=packet.data.get('key'))
                    
                    # Process any buffered packets
                    self.process_buffered_packets()
                elif msg_type == "complete":
                    # QKD completion signal received
                    self.logger.info(f"QKD completion signal received at {self.name}")
                    self._send_update(
                        SimulationEventType.INFO,
                        data=dict(
                            type="qkd_complete",
                            message=f"QKD completed successfully at {self.name}"
                        )
                    )
                    # Mark QKD as completed
                    self.qkd_in_progress = False
                    # Process any buffered packets
                    self.process_buffered_packets()
                elif msg_type == "reconcile_bases":
                    self._send_update(
                        SimulationEventType.INFO,
                        data=dict(
                            type="qkd_progress",
                            message=f"Reconciling bases at {self.name}"
                        )
                    )
                elif msg_type == "estimate_error_rate":
                    self._send_update(
                        SimulationEventType.INFO,
                        data=dict(
                            type="qkd_progress",
                            message=f"Estimating error rate at {self.name}"
                        )
                    )
                    
            except Exception as e:
                self.logger.error(f"Error processing QKD control message: {e}")
                return
                
            # Forward QKD control message to quantum host
            self.local_quantum_host.receive_classical_data(packet.data)
        else:
            # Handle packets that need encryption
            if self.shared_key is None and self.paired_adapter is not None:
                self.logger.info(f"No shared key available at {self.name}, buffering packet")
                self.input_data_buffer.put(packet)
                
                # Only initiate QKD if not already in progress
                if not self.qkd_in_progress:
                    self.initiate_qkd()
                return

            # If the packet is for the paired adapter, check if a key exists and then encrypt and forward
            if self.paired_adapter and packet.to_address == self.local_classical_router:
                if self.shared_key:
                    packet = self.encrypt_packet(packet)
                    self._send_update(SimulationEventType.DATA_ENCRYPTED, cipher=packet.data, algorithm="XOR")
                    self.forward_packet(packet, self.paired_adapter.local_classical_router)
                else:
                    print(
                        f"Time: {self.network.world.time:.2f}, {self.name} cannot forward packet, no shared key with {self.paired_adapter.name}"
                    )
            else:
                # Otherwise, forward the packet normally
                self.forward_packet(packet, self.paired_adapter.local_classical_router)
        self._send_update(SimulationEventType.DATA_RECEIVED, packet=packet)

    def encrypt_packet(self, packet: ClassicDataPacket):
        encrypted_data = simple_xor_encrypt(packet.data, self.shared_key)
        self.logger.debug(f"Encrypted Data: {packet.data} -> {encrypted_data}")
        
        return ClassicDataPacket(
            data=encrypted_data,
            from_address=packet.from_address,
            to_address=self.paired_adapter.local_classical_router,
            type=packet.type,
            protocol=packet.protocol,
            time=packet.time,
            name=packet.name,
            description=packet.description,
            destination_address=packet.destination_address,
        )

    def decrypt_packet(self, packet: ClassicDataPacket):
        decrypted_data = simple_xor_decrypt(packet.data, self.shared_key)
        self.logger.debug(f"Decrypted Data: {packet.data} -> {decrypted_data}")

        return ClassicDataPacket(
            data=decrypted_data,
            from_address=packet.from_address,
            to_address=packet.destination_address or packet.to_address,
            type=packet.type,
            protocol=packet.protocol,
            time=packet.time,
            name=packet.name,
            description=packet.description,
        )

    def process_packet(self, packet: ClassicDataPacket):
        """Process and forward classical data packets."""
        if self.shared_key:
            # Decrypt and forward the packet
            packet = self.decrypt_packet(packet)
            self._send_update(SimulationEventType.DATA_DECRYPTED, data=packet.data, algorithm="XOR")
            self.logger.info(f"Successfully decrypted packet at {self.name}")
            
            # Determine final destination
            forward_to = packet.destination_address or packet.to_address
            
            # Forward the packet
            self.forward_packet(packet, forward_to)
            self._send_update(
                SimulationEventType.INFO,
                data=dict(
                    type="packet_forwarded",
                    message=f"Forwarded decrypted packet to {forward_to}",
                    from_adapter=self.name,
                    to_destination=str(forward_to),
                    packet_data=packet.data
                )
            )
        else:
            self.logger.warning(f"Time: {self.network.world.time:.2f}, {self.name} cannot process packet, no shared key")
            # Buffer the packet and initiate QKD if needed
            if self.paired_adapter:
                self.logger.info(f"Buffering packet and initiating QKD with {self.paired_adapter.name}")
                self.input_data_buffer.put(packet)
                self.initiate_qkd()
                
    def process_buffered_packets(self):
        """Process any packets that were buffered while waiting for QKD completion."""
        self.logger.info(f"Processing buffered packets at {self.name}")
        while not self.input_data_buffer.empty():
            packet = self.input_data_buffer.get()
            self.process_packet(packet)

    def send_classical_data(self, data):

        conn = self.local_classical_router.get_connection(
            self.local_classical_router, self.paired_adapter.local_classical_router
        )

        if not conn:
            raise NotConnectedError(self, self.paired_adapter.local_classical_router)

        packet = QKDTransmissionPacket(
            data=data,
            from_address=self.local_classical_router,
            to_address=self.paired_adapter.local_classical_router,
            type=PacketType.DATA,
        )
        conn.transmit_packet(packet)

    def forward(self):
        self.local_classical_router.forward()

    def intercept_route_packet(self, packet: ClassicDataPacket):
        self.receive_packet(packet)

    def forward_packet(self, packet: ClassicDataPacket, to):
        packet.append_hop(self.local_classical_router)
        self.logger.info(f"Forwarding packet from {self.name} to {to}")
        
        # Get direct connection if available
        direct_connection = self.local_classical_router.get_connection(
            self.local_classical_router, to
        )

        if direct_connection:
            self.logger.debug(f"Direct connection found between {self.name} and {to}")
            packet.next_hop = to
            
            # Handle MTU fragmentation if needed
            if direct_connection.mtu != -1 and packet.size_bytes > direct_connection.mtu:
                self.logger.info(f"Fragmenting packet due to MTU limit: {direct_connection.mtu}")
                fragments = fragment_packet(packet, direct_connection.mtu)
                self._send_update(
                    SimulationEventType.INFO,
                    data=dict(
                        type=InfoEventType.PACKET_FRAGMENTED,
                        message=f"Packet fragmented into {len(fragments)} fragments due to MTU limit of {direct_connection.mtu} bytes."
                    )
                )
                for fragment in fragments:
                    direct_connection.transmit_packet(fragment)
                    self.logger.debug(f"Transmitted fragment to {to}")
            else:
                direct_connection.transmit_packet(packet)
                self.logger.debug(f"Transmitted packet to {to}")
            return
        
        try:
            shortest_path = self.local_classical_router.default_gateway.get_path(
                self.local_classical_router, packet.to_address
            )
            
            if len(shortest_path) <= 1:
                raise NotConnectedError(self.local_classical_router, packet.to_address)
            
            next_hop = shortest_path[1]
            self.logger.info(f"Routing packet via {next_hop} to reach {packet.to_address}")
            
            packet.next_hop = next_hop
            next_connection = self.local_classical_router.get_connection(
                self.local_classical_router, next_hop
            )
            
            if not next_connection:
                raise NotConnectedError(self.local_classical_router, next_hop)
            
            # Handle MTU fragmentation for indirect routes
            if next_connection.mtu != -1 and packet.size_bytes > next_connection.mtu:
                self.logger.info(f"Fragmenting packet for indirect route via {next_hop}")
                fragments = fragment_packet(packet, next_connection.mtu)
                self._send_update(
                    SimulationEventType.INFO,
                    data=dict(
                        type=InfoEventType.PACKET_FRAGMENTED,
                        message=f"Packet fragmented into {len(fragments)} fragments for transmission via {next_hop}"
                    )
                )
                for fragment in fragments:
                    next_connection.transmit_packet(fragment)
                    self.logger.debug(f"Transmitted fragment to {next_hop}")
            else:
                next_connection.transmit_packet(packet)
                self.logger.debug(f"Transmitted packet to {next_hop}")
                
        except Exception as e:
            self.logger.error(f"Error forwarding packet: {str(e)}")
            raise

    def __name__(self):
        return f"QuantumAdapter - '{self.name}'"

    def __repr__(self):
        return self.__name__()
