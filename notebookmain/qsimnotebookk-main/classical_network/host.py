
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from classical_network.connection import ClassicConnection
from classical_network.enum import PacketType
from classical_network.node import ClassicalNode
from classical_network.packet import ClassicDataPacket
from classical_network.router import ClassicalRouter
from core.base_classes import Node, World, Zone
from core.enums import NodeType, SimulationEventType
from core.exceptions import DefaultGatewayNotFound, NotConnectedError
from core.network import Network

if TYPE_CHECKING:
    from quantum_network.adapter import QuantumAdapter


class ClassicalHost(ClassicalNode):
    def __init__(
        self,
        address: str,
        location: Tuple[int, int],
        network: Network,
        zone: Zone | World = None,
        name="",
        description="",
    ):
        super().__init__(
            NodeType.CLASSICAL_HOST, location, address, network, zone, name, description
        )
        self.default_gateway: ClassicalHost | ClassicalRouter = None
        self.quantum_adapter: QuantumAdapter = None

    def add_connection(self, connection: ClassicConnection):
        super().add_connection(connection)
        if self.default_gateway == None:
            self.default_gateway = connection.node_2

        # Use Router
        if isinstance(connection.node_2, ClassicalRouter):
            self.default_gateway = connection.node_2

        if isinstance(connection.node_1, ClassicalRouter):
            self.default_gateway = connection.node_1

    def forward(self):
        for node_2, buffer in self.buffers.items():
            while not buffer.empty():
                packet = buffer.get()

                if packet.to_address == self:
                    self.recive_packet(packet)
                else:
                    self.logger.warn(f"Unexpected packet '{packet}' received from {node_2}")

    def recive_packet(self, packet: ClassicDataPacket):
        self._send_update(SimulationEventType.PACKET_RECEIVED, packet=packet)
        if packet.type == PacketType.DATA:
            self.receive_data(packet.data)

    def add_quantum_adapter(self, adapter: QuantumAdapter):
        self.quantum_adapter = adapter

    def send_data(self, data, send_to: "ClassicalHost"):
        if self.quantum_adapter:
            to_address = self.quantum_adapter.local_classical_router
            destination_address = send_to
        else:
            to_address = send_to
            destination_address = None
        packet = ClassicDataPacket(
            data,
            self,
            to_address,
            PacketType.DATA,
            destination_address=destination_address,
        )

        conn = self.get_connection(self, send_to)
        if conn:
            packet.next_hop = send_to
        else:
            if not self.default_gateway:
                raise DefaultGatewayNotFound(self)
            self.logger.debug(f'Sending to default gateway')
            packet.next_hop = self.default_gateway

        conn = self.get_connection(self, packet.next_hop)

        if not conn:
            raise NotConnectedError(self, packet.next_hop)

        conn.transmit_packet(packet)
        self._send_update(SimulationEventType.DATA_SENT, data=data, destination=destination_address)

    def receive_data(self, data):
        self._send_update(SimulationEventType.DATA_RECEIVED, data=data)

    def __name__(self):
        return f"Host - '{self.name}'"

    def __repr__(self):
        return self.__name__()
