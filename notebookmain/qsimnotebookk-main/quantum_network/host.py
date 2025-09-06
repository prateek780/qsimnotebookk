import random
import time
from typing import Any, Callable, List, Tuple
import qutip as qt
from core.base_classes import World, Zone
from core.enums import NodeType, SimulationEventType
from core.exceptions import QuantumChannelDoesNotExists
from core.network import Network
from quantum_network.channel import QuantumChannel
from quantum_network.node import QuantumNode


class QuantumHost(QuantumNode):
    def __init__(
        self,
        address: str,
        location: Tuple[int, int],
        network: Network,
        zone: Zone | World = None,
        send_classical_fn: Callable[[Any], None] = None,
        qkd_completed_fn: Callable[[List[int]], None] = None,
        num_bits = 16,
        name="",
        description="",
    ):
        super().__init__(
            NodeType.QUANTUM_HOST, location, network, address, zone, name, description
        )
        self.quantum_channels: list[QuantumChannel] = []
        self.entangled_nodes = {}  # Nodes that this node is entangled with
        self.basis_choices = []
        self.measurement_outcomes = []
        self.num_bits = num_bits
        self.qkd_in_progress = False  # Track if QKD is currently in progress
        self.shared_bases_indices = []
        
        if send_classical_fn:
            self.send_classical_data = send_classical_fn
        
        if qkd_completed_fn:
            self.qkd_completed_fn = qkd_completed_fn

    def add_quantum_channel(self, channel):
        self.quantum_channels.append(channel)

    def channel_exists(self, to_host: QuantumChannel):
        for chan in self.quantum_channels:
            if (chan.node_1 == self and chan.node_2 == to_host) or (chan.node_2 == self and chan.node_1 == to_host):
                return chan

    def get_channel(self, to_host=None):
        """Get quantum channel to specified host or first available channel"""
        if to_host is None:
            return self.quantum_channels[0] if self.quantum_channels else None
        
        for chan in self.quantum_channels:
            if (chan.node_1 == self and chan.node_2 == to_host) or (chan.node_2 == self and chan.node_1 == to_host):
                return chan
        return None

    def forward(self):
        while not self.qmemeory_buffer.empty():
            qbit = self.qmemeory_buffer.get()
            self.process_received_qbit(qbit)

    def send_qubit(self, qubit, channel: QuantumChannel):
        # Apply noise to the qubit based on channel properties (using QuTiP)
        channel.transmit_qubit(qubit, self)
        self.qmemory = None

    def generate_entanglement(self, with_node: QuantumNode, channel: QuantumChannel):
        # Generate a Bell pair using QuTiP
        bell_state = qt.bell_state("00")

        # Assign one qubit to self and one to the other node
        self.qmemory = qt.ptrace(bell_state, 0)  # Keep first qubit
        with_node.qmemory = qt.ptrace(bell_state, 1)  # Send second qubit

        # Store information about the entangled node
        self.entangled_nodes[with_node.address] = channel
        with_node.entangled_nodes[self.address] = channel

        # Send the second qubit to the other node via the channel
        self.send_qubit(with_node.qmemory, channel)

    def prepare_qubit(self, basis, bit):
        """Prepares a qubit in the given basis and bit value using QuTiP."""
        if basis == "Z":
            if bit == 0:
                qubit = qt.basis(2, 0)  # |0>
            else:
                qubit = qt.basis(2, 1)  # |1>
        else:  # basis == "X"
            if bit == 0:
                qubit = (qt.basis(2, 0) + qt.basis(2, 1)).unit()  # |+>
            else:
                qubit = (qt.basis(2, 0) - qt.basis(2, 1)).unit()  # |->
        return qubit

    def measure_qubit(self, qubit, basis):
        """Measures the qubit in the given basis using QuTiP."""
        if basis == "Z":
            # Measurement in the computational basis
            projector0 = qt.ket2dm(qt.basis(2, 0))  # Projector onto |0>
            projector1 = qt.ket2dm(qt.basis(2, 1))  # Projector onto |1>
        else:  # basis == "X"
            # Measurement in the Hadamard basis
            projector0 = qt.ket2dm(
                (qt.basis(2, 0) + qt.basis(2, 1)).unit()
            )  # Projector onto |+>
            projector1 = qt.ket2dm(
                (qt.basis(2, 0) - qt.basis(2, 1)).unit()
            )  # Projector onto |->

        # Calculate probabilities using the expectation value
        prob0 = qt.expect(projector0, qubit)
        prob1 = qt.expect(projector1, qubit)

        # Choose outcome based on probabilities
        outcome = 0 if random.random() < prob0 else 1
        return outcome

    def process_received_qbit(self, qbit):
        self.set_qmemory(qbit)
        
        basis = random.choice(["Z", "X"])
        
        outcome = self.measure_qubit(qbit, basis)
        
        self.basis_choices.append(basis)
        self.measurement_outcomes.append(outcome)
        
        if len(self.measurement_outcomes) == self.num_bits:
            self.send_bases_for_reconsile()
            
    def send_bases_for_reconsile(self):
        self.send_classical_data({
            'type': 'reconcile_bases',
            'data': self.basis_choices
        })
        
    def receive_classical_data(self, message):
        """Handle classical messages during QKD protocol."""
        self.logger.debug(f"Received Classical Data at host {self}. Data => {message}")
        
        if not isinstance(message, dict):
            self.logger.error(f"Invalid message format received: {message}")
            return
            
        msg_type = message.get("type", "unknown")
        self.logger.info(f"Processing message type: {msg_type}")
        
        try:
            if msg_type == "reconcile_bases":
                self.bb84_reconcile_bases(message["data"])
                self._send_update(
                    SimulationEventType.INFO,
                    data=dict(
                        type="qkd_progress",
                        message=f"Reconciling bases at {self.name}"
                    )
                )
                
            elif msg_type == "estimate_error_rate":
                self.bb84_estimate_error_rate(message["data"])
                self._send_update(
                    SimulationEventType.INFO,
                    data=dict(
                        type="qkd_progress",
                        message=f"Estimating error rate at {self.name}"
                    )
                )
                
            elif msg_type == "complete":
                self.logger.info("QKD process completing, extracting final key")
                raw_key = self.bb84_extract_key()
                if self.qkd_completed_fn:
                    self.qkd_completed_fn(raw_key)
                self.reset_qkd_state()  # Reset state after successful completion
                self._send_update(
                    SimulationEventType.INFO,
                    data=dict(
                        type="qkd_complete",
                        message=f"QKD completed successfully at {self.name}"
                    )
                )
                
            elif msg_type == "shared_bases_indices":
                self.update_shared_bases_indices(message["data"])
                self._send_update(
                    SimulationEventType.INFO,
                    data=dict(
                        type="qkd_progress",
                        message=f"Processing shared bases indices at {self.name}"
                    )
                )
            
            self._send_update(SimulationEventType.DATA_RECEIVED, message=message)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            self.reset_qkd_state()  # Reset state on error
            
    def update_shared_bases_indices(self, shared_base_indices):
        """Update shared bases indices and initiate error rate estimation."""
        self.shared_bases_indices = shared_base_indices
        self.logger.info(f"Received {len(shared_base_indices)} shared bases indices")
        
        # Choose random bits for error estimation (up to 25% of matching bases)
        random_bit_number = min(len(shared_base_indices) // 4, 
                              max(2, self.num_bits // 4))
        
        # Select random indices from shared bases for error checking
        random_indices = random.sample(shared_base_indices, random_bit_number)
        random_error_calculation_bit = [
            (self.measurement_outcomes[i], i) for i in random_indices
        ]
        
        self.logger.info(f"Selected {len(random_error_calculation_bit)} bits for error estimation")
        
        # Send bits for error rate estimation
        self.send_classical_data({
            'type': 'estimate_error_rate',
            'data': random_error_calculation_bit
        })
        
    def bb84_send_qubits(self):
        """Sends a sequence of qubits for the BB84 protocol."""
        self.basis_choices = []  # Reset the basis choices
        if not self.quantum_channels:
            raise QuantumChannelDoesNotExists(self)
        
        channel = self.quantum_channels[0]
        for _ in range(self.num_bits):
            basis = random.choice(["Z", "X"])
            bit = random.choice([0, 1])
            self.basis_choices.append(basis)
            self.measurement_outcomes.append(bit)
            qubit = self.prepare_qubit(basis, bit)
            self.send_qubit(qubit, channel)

        # Send basis choices to the destination host (classical communication)
        # self.send_classical_data(
        #     {"type": "basis_choices", "data": self.basis_choices}
        # )

    def bb84_reconcile_bases(self, their_bases):
        """Performs basis reconciliation."""
        self.shared_bases_indices = [
            i
            for i, (b1, b2) in enumerate(zip(self.basis_choices, their_bases))
            if b1 == b2
        ]

        # Send confirmation of shared bases (classical communication)
        self.send_classical_data(
            {
                "type": "shared_bases_indices",
                "data": self.shared_bases_indices,
                "sender": self,
            },
        )

    def bb84_estimate_error_rate(self, their_bits_sample):
        """Estimates the error rate by comparing a sample of bits."""
        num_errors = 0
        for their_bit, i in their_bits_sample:
            if self.measurement_outcomes[i] != their_bit:
                num_errors += 1
        error_rate = num_errors / len(their_bits_sample) if len(their_bits_sample) > 0 else 0

        print(f"🔍 Error rate estimation: {error_rate:.1%} ({num_errors}/{len(their_bits_sample)} errors)")
        
        # Send completion signal to notify adapters
        self.send_classical_data({
            'type': 'complete'
        })
        
        # Extract the final shared key
        raw_key = self.bb84_extract_key()
        
        # Mark QKD as completed
        self.qkd_in_progress = False
        
        # Call the completion callback if available
        if self.qkd_completed_fn:
            self.qkd_completed_fn(raw_key)
            
        print(f"🔑 QKD completed! Shared key: {len(raw_key)} bits")
        return error_rate
        

    def bb84_extract_key(self):
        """Extracts a shared key based on the reconciliation information."""
        shared_key = [self.measurement_outcomes[i] for i in self.shared_bases_indices]
        return shared_key
    
    def perform_qkd(self):
        """Initiate the BB84 QKD protocol if not already in progress."""
        if self.qkd_in_progress:
            self.logger.warning("QKD already in progress, skipping new request")
            return
            
        self.logger.info("Starting BB84 QKD protocol")
        self.qkd_in_progress = True
        self.basis_choices = []
        self.measurement_outcomes = []
        self.shared_bases_indices = []
        
        try:
            # Start the BB84 protocol by sending qubits
            self.bb84_send_qubits()
            
            # The rest of the protocol (reconciliation, error checking) 
            # will be handled by the quantum channel and classical communication
            # This method just initiates the process
            
        except Exception as e:
            self.logger.error(f"Error during QKD: {str(e)}")
            self.qkd_in_progress = False
            raise

    def reset_qkd_state(self):
        """Reset the QKD state after completion or failure."""
        self.qkd_in_progress = False
        self.basis_choices = []
        self.measurement_outcomes = []
        self.shared_bases_indices = []
        self.logger.info("QKD state reset")

    def __name__(self):
        return f"QuantumHost - '{self.name}'"

    def __repr__(self):
        return self.__name__()