from queue import Queue
from typing import List, Tuple

# qutip is optional here; safe to keep the import if your env has it
try:
    import qutip as qt  # noqa: F401
except Exception:
    qt = None

from classical_network.connection import ClassicConnection
from classical_network.enum import PacketType
from classical_network.packet import ClassicDataPacket
from classical_network.router import ClassicalRouter
from core.base_classes import Node, World, Zone
from core.enums import NodeType, NetworkType, SimulationEventType
from core.exceptions import (
    DefaultGatewayNotFound,
    NotConnectedError,
    PairAdapterAlreadyExists,
    PairAdapterDoesNotExists,
    QuantumChannelDoesNotExists,
    UnSupportedNetworkError,
)
from core.network import Network

from quantum_network.interactive_host import InteractiveQuantumHost as QuantumHost
from quantum_network.packet import QKDTransmissionPacket
from utils.simple_encryption import simple_xor_decrypt, simple_xor_encrypt


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

        # QKD state
        self.shared_key: List[int] | None = None
        self._qkd_in_progress: bool = False

        # Local quantum host
        self.local_quantum_host: QuantumHost = quantum_host
        # Wire host <-> adapter bridge
        self.local_quantum_host.send_classical_data = self.send_classical_data
        self.local_quantum_host.qkd_completed_fn = self.on_qkd_established
        if hasattr(self.local_quantum_host, "set_adapter"):
            try:
                self.local_quantum_host.set_adapter(self)
            except Exception:
                pass

        # Internal classical router
        self.local_classical_router = ClassicalRouter(
            f"InternalQCRouter{self.name}",
            self.location,
            self.classical_network,
            self.zone,
            f"QC_Router_{self.name}",
        )
        # Intercept to apply enc/dec transparently
        self.local_classical_router.route_packet = self.intercept_route_packet

        # Pairing
        self.paired_adapter: "QuantumAdapter" | None = paired_adapter
        if paired_adapter:
            connection = ClassicConnection(
                self.local_classical_router,
                self.paired_adapter.local_classical_router,
                10,
                10,
                name="QC_Router_Connection",
            )
            self.local_classical_router.add_connection(connection)
            self.paired_adapter.local_classical_router.add_connection(connection)

        # Ensure a quantum channel exists between hosts
        if paired_adapter and (
            not self.local_quantum_host.channel_exists(
                paired_adapter.local_quantum_host
            )
        ):
            raise QuantumChannelDoesNotExists(self)

    def add_paired_adapter(self, adapter: "QuantumAdapter"):
        """Pair after construction; also wire classical link and verify quantum channel."""
        if self.paired_adapter:
            raise PairAdapterAlreadyExists(self, self.paired_adapter)

        self.paired_adapter = adapter

        # Build classical connection in both routers
        connection = ClassicConnection(
            self.local_classical_router,
            adapter.local_classical_router,
            10,
            10,
            name="QC_Router_Connection",
        )
        self.local_classical_router.add_connection(connection)
        adapter.local_classical_router.add_connection(connection)

        # Ensure quantum channel exists between hosts
        if not self.local_quantum_host.channel_exists(adapter.local_quantum_host):
            raise QuantumChannelDoesNotExists(self)

    def on_qkd_established(self, key: List[int]):
        """Callback from host when QKD completes."""
        self.shared_key = key
        self.logger.debug(f"QKD Established {key}")

        # Flush buffered packets now that we can decrypt/encrypt
        while not self.input_data_buffer.empty():
            packet = self.input_data_buffer.get()
            self.receive_packet(packet)

    def calculate_distance(self, node1, node2):
        x1, y1 = node1.location
        x2, y2 = node2.location
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def initiate_qkd(self):
        """Start QKD with the paired adapter, safely and only once at a time."""
        if self._qkd_in_progress or self.shared_key is not None:
            return

        if not self.paired_adapter:
            self.logger.debug(f"{self.name} has no paired adapter to perform QKD.")
            raise PairAdapterDoesNotExists(self)

        host = getattr(self, "local_quantum_host", None)
        if host is None:
            raise RuntimeError(f"{self.name}: QKD cannot start, local_quantum_host is None")

        # Validate student implementation; try to autowire if needed
        validated = getattr(host, "student_code_validated", False)
        if not validated:
            try:
                if hasattr(host, "try_autowire_student") and host.try_autowire_student():
                    validated = getattr(host, "student_code_validated", False)
                elif hasattr(host, "validate_student_implementation"):
                    host.validate_student_implementation()
                    validated = getattr(host, "student_code_validated", False)
            except Exception as e:
                print(f"❌ {self.name}: Autowire/validation failed: {e}")
                validated = False

        if not validated:
            raise RuntimeError(
                f"{self.name}: QKD cannot start, student implementation not validated. "
                f"Make sure your BB84 code is properly implemented and attached."
            )

        self._qkd_in_progress = True
        try:
            self.local_quantum_host.perform_qkd()
            self._send_update(
                SimulationEventType.QKD_INITIALIZED, with_adapter=self.paired_adapter
            )
        finally:
            self._qkd_in_progress = False

    def receive_packet(self, packet: ClassicDataPacket | QKDTransmissionPacket):
        """
        Adapter ingress for classical data and QKD control messages.
        - Classical from paired adapter (encrypted): decrypt & forward.
        - QKDTransmissionPacket: pass to host.
        - Otherwise: kick off QKD if needed, then encrypt/forward appropriately.
        """
        print(f"📥 {self.name}: Received packet: {type(packet).__name__} - {packet.data if hasattr(packet, 'data') else 'No data'}")
        
        # 1) QKD control over classical link → host (check this FIRST since QKDTransmissionPacket inherits from ClassicDataPacket)
        if isinstance(packet, QKDTransmissionPacket):
            print(f"🔍 {self.name}: Processing QKDTransmissionPacket - passing to quantum host")
            print(f"🔍 {self.name}: Packet data: {packet.data}")
            self.local_quantum_host.receive_classical_data(packet.data)
            print(f"✅ {self.name}: QKDTransmissionPacket processed successfully")
        
        # 2) Encrypted classical from peer → decrypt/process
        elif (
            isinstance(packet, ClassicDataPacket)
            and self.paired_adapter is not None
            and len(packet.hops) >= 2
            and packet.hops[-2] == self.paired_adapter.local_classical_router
        ):
            print(f"🔍 {self.name}: Processing ClassicDataPacket (encrypted from peer)")
            self.process_packet(packet)

        else:
            print(f"🔍 {self.name}: Processing packet in else clause")
            # 3) No key yet: start QKD once and buffer packet
            if self.shared_key is None and self.paired_adapter is not None:
                print(f"🔍 {self.name}: No shared key, buffering packet")
                if not self._qkd_in_progress:
                    self.initiate_qkd()
                self.input_data_buffer.put(packet)
                return

            # 4) If destined to the paired adapter, encrypt then forward
            if (
                self.paired_adapter is not None
                and packet.to_address == self.paired_adapter.local_classical_router
            ):
                if self.shared_key:
                    enc = self.encrypt_packet(packet)
                    self.forward_packet(enc, self.paired_adapter.local_classical_router)
                else:
                    import time
                    print(
                        f"Time: {time.time():.2f}, {self.name} cannot forward packet, "
                        f"no shared key with {self.paired_adapter.name}"
                    )
            else:
                # 5) Otherwise, forward toward its intended next hop
                self.forward_packet(packet, packet.to_address)

        self._send_update(SimulationEventType.DATA_RECEIVED, packet=packet)

    def encrypt_packet(self, packet: ClassicDataPacket) -> ClassicDataPacket:
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

    def decrypt_packet(self, packet: ClassicDataPacket) -> ClassicDataPacket:
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
        """Decrypt and forward decrypted classical packet if we have a key."""
        if self.shared_key:
            dec = self.decrypt_packet(packet)
            # Forward decrypted packet to its intended classical destination
            self.forward_packet(dec, dec.to_address)
        else:
            import time
            print(
                f"Time: {time.time():.2f}, {self.name} cannot process packet, no shared key"
            )

    def send_classical_data(self, data):
        """Called by the quantum host to send QKD control/classical data."""
        print(f"📤 {self.name}: Sending classical data: {data}")
        if self.paired_adapter is None:
            raise PairAdapterDoesNotExists(self)

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
        """Advance internal classical router events."""
        self.local_classical_router.forward()

    def intercept_route_packet(self, packet: ClassicDataPacket):
        """Router hook to allow the adapter to examine and process packets."""
        self.receive_packet(packet)

    def forward_packet(self, packet: ClassicDataPacket, to):
        """Forward a packet to a directly connected neighbor or via default gateway."""
        packet.append_hop(self.local_classical_router)

        direct_connection = self.local_classical_router.get_connection(
            self.local_classical_router, to
        )
        if direct_connection:
            packet.next_hop = packet.to_address
            direct_connection.transmit_packet(packet)
            return

        # Fall back to shortest path via default gateway
        shortest_path = self.local_classical_router.default_gateway.get_path(
            self.local_classical_router, packet.to_address
        )
        if len(shortest_path) <= 1:
            raise NotConnectedError(self.local_classical_router, packet.to_address)

        next_hop = shortest_path[1]
        packet.next_hop = next_hop
        next_connection = self.local_classical_router.get_connection(
            self.local_classical_router, next_hop
        )
        if not next_connection:
            raise NotConnectedError(self.local_classical_router, next_hop)

        next_connection.transmit_packet(packet)

    def _name_(self):
        return f"QuantumAdapter - '{self.name}'"

    def attach_student_implementation(self, student_impl):
        """Helper method to attach student implementation to the quantum host."""
        if not self.local_quantum_host:
            print(f"❌ {self.name}: No quantum host available to attach student implementation")
            return False

        if hasattr(self.local_quantum_host, "attach_student"):
            ok = self.local_quantum_host.attach_student(student_impl)
            if ok:
                print(f"✅ {self.name}: Student implementation attached successfully")
            else:
                print(f"❌ {self.name}: Student implementation attach() returned False")
            return ok

        self.local_quantum_host.student_implementation = student_impl
        print(f"✅ {self.name}: Student implementation set directly")
        return True

    def _repr_(self):
        return self._name_()