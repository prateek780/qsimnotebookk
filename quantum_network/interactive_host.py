"""
Interactive Quantum Host for Student Learning
===========================================

This module provides an interactive quantum host implementation that students
can modify and extend for learning quantum networking protocols. It replaces
the hardcoded host.py with a more educational and flexible approach.
"""

from __future__ import annotations

import random
import time
import traceback
from typing import Any, Callable, List, Tuple, Optional
import importlib
try:
    import qutip as qt
except Exception:
    qt = None
from core.base_classes import World, Zone
from core.enums import InfoEventType, NodeType, SimulationEventType
from core.exceptions import QuantumChannelDoesNotExists
from core.network import Network
from quantum_network.channel import QuantumChannel
from quantum_network.node import QuantumNode
from quantum_network.repeater import QuantumRepeater


class InteractiveQuantumHost(QuantumNode):
    """
    Interactive Quantum Host for educational purposes.
    
    This host REQUIRES students to implement quantum protocols before simulation can run.
    The simulation will only work after students have "vibe coded" their BB84 algorithms.
    
    Students must implement:
    - BB84 quantum key distribution
    - Quantum entanglement protocols
    - Custom quantum networking protocols
    
    Without student implementations, the host will refuse to operate.
    """
    
    def __init__(
        self,
        address: str,
        location: Tuple[int, int],
        network: Network,
        zone: Zone | World = None,
        send_classical_fn: Callable[[Any], None] = None,
        qkd_completed_fn: Callable[[List[int]], None] = None,
        name="",
        description="",
        protocol: str = "bb84",
        student_implementation: Optional[object] = None,
        require_student_code: bool = True
    ):
        super().__init__(
            NodeType.QUANTUM_HOST, location, network, address, zone, name, description
        )
        
        self.protocol = protocol
        self.student_implementation = student_implementation
        self.require_student_code = require_student_code
        
        # Protocol state
        self.quantum_channels: List[QuantumChannel] = []
        self.entangled_nodes = {}
        self.basis_choices = []
        self.measurement_outcomes = []
        self.shared_bases_indices = []
        self._reconcile_sent = False
        
        # Educational validation
        self.student_code_validated = False
        self.required_methods = ['bb84_send_qubits', 'process_received_qbit', 'bb84_reconcile_bases', 'bb84_estimate_error_rate']
        
        # Entanglement attributes
        self.entangled_qubit: 'qt.Qobj' | None = None
        self.entanglement_partner_address: str | None = None
        self.entangled_channel: QuantumChannel | None = None
        
        # Callback functions (initialize attributes to safe defaults)
        self.send_classical_data = send_classical_fn if send_classical_fn else (lambda message: None)
        self.qkd_completed_fn = qkd_completed_fn if qkd_completed_fn else None
        
        # Learning metrics
        self.learning_stats = {
            'qubits_sent': 0,
            'qubits_received': 0,
            'successful_protocols': 0,
            'error_rates': []
        }
        
        print(f" Interactive Quantum Host '{name}' created!")
        print(f" Protocol: {protocol}")
        
        # ENFORCE STUDENT CODE REQUIREMENT - NO EXCEPTIONS!
        if not student_implementation:
            # Try to load a student plugin from file, exported by the notebook
            if self._load_student_plugin_from_file():
                print(" Loaded student implementation plugin from file")
                self.validate_student_implementation()
            else:
                print(" STUDENT IMPLEMENTATION REQUIRED!")
                print(" VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION")
                print(" This simulation will NOT work without student BB84 code!")
                print(" Export your student implementation plugin from the notebook to enable the simulation.")
                print(" Open quantum_networking_interactive.ipynb for the export helper cell.")
                print(" No hardcoded fallbacks available!")
                self.student_code_validated = False
        else:
            print(f" Using student implementation: {type(student_implementation).__name__}")
            self.validate_student_implementation()
            # Ensure bridges/plugins that expect a back-reference get it
            try:
                if hasattr(self.student_implementation, 'host') and getattr(self.student_implementation, 'host', None) is None:
                    self.student_implementation.host = self
            except Exception:
                pass
            
        # Force require_student_code to always be True - no exceptions!
        self.require_student_code = True

    def check_notebook_implementation(self):
        """Check if student has completed implementation in notebook"""
        try:
            import json
            import os
            
            # Check for student implementation status file
            status_file = "student_implementation_status.json"
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    status = json.load(f)
                
                if status.get("student_implementation_ready", False):
                    print(" Found student implementation from notebook!")
                    return True
            
            return False
        except Exception as e:
            print(f" Could not check notebook implementation: {e}")
            return False

    def validate_student_implementation(self):
        """Validate that student has implemented required methods"""
        print(f"🔍 VALIDATE_STUDENT_IMPLEMENTATION called")
        print(f"   student_implementation: {self.student_implementation}")
        print(f"   required_methods: {self.required_methods}")
        
        if not self.student_implementation:
            print("❌ No student implementation provided")
            self.student_code_validated = False
            return False
        
        missing_methods = []
        for method_name in self.required_methods:
            has_method = hasattr(self.student_implementation, method_name)
            print(f"   Checking method '{method_name}': {has_method}")
            if not has_method:
                missing_methods.append(method_name)
        
        if missing_methods:
            print(f"❌ Student implementation missing methods: {missing_methods}")
            print(" Implement these methods to enable quantum protocols")
            self.student_code_validated = False
            return False
        else:
            print("✅ Student implementation validated! Quantum protocols enabled.")
            self.student_code_validated = True
            return True

    def _load_student_plugin_from_file(self) -> bool:
        """Attempt to load a student implementation plugin written by the notebook.
        Expects a status file 'student_implementation_status.json' with keys
        'student_plugin_module' and 'student_plugin_class'.
        The plugin class should accept the host in its constructor: Plugin(host).
        """
        try:
            import os
            import json
            status_file = "student_implementation_status.json"
            if not os.path.exists(status_file):
                print("📄 No student implementation status file found")
                return False
                
            with open(status_file, "r") as f:
                status = json.load(f)
                
            if not status.get("student_implementation_ready", False):
                print("📄 Student implementation not marked as ready")
                return False
                
            module_name = status.get("student_plugin_module")
            class_name = status.get("student_plugin_class")
            
            if not module_name or not class_name:
                print("📄 Missing module or class name in status file")
                return False
                
            print(f"🔌 Loading student plugin: {module_name}.{class_name}")
            module = importlib.import_module(module_name)
            plugin_cls = getattr(module, class_name, None)
            
            if plugin_cls is None:
                print(f"📄 Class {class_name} not found in module {module_name}")
                return False
                
            self.student_implementation = plugin_cls(self)
            print(f"✅ Student plugin loaded successfully: {class_name}")
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to load student plugin: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Removed hardcoded notebook adapter. Only student-provided implementations are allowed.

    def check_student_implementation_required(self, operation_name):
        """Check if student implementation is required for this operation"""
        print(f"🔍 CHECK_STUDENT_IMPLEMENTATION_REQUIRED for '{operation_name}'")
        print(f"   require_student_code: {self.require_student_code}")
        print(f"   student_code_validated: {self.student_code_validated}")
        print(f"   has student_implementation: {self.student_implementation is not None}")
        
        if self.require_student_code and not self.student_code_validated:
            print(f"❌ Cannot perform '{operation_name}' - Student implementation required!")
            print(" VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION")
            print(" Steps to enable:")
            print("1. Open the Jupyter notebook (quantum_networking_interactive.ipynb)")
            print("2. Implement your BB84 algorithms using the provided hints")
            print("3. Create a StudentImplementation class with required methods")
            print("4. Connect your implementation to the simulation")
            print(" See the notebook for detailed implementation examples!")
            return False
        print(f"✅ Student implementation check passed for '{operation_name}'")
        return True

    def add_quantum_channel(self, channel):
        """Add a quantum channel to this host"""
        self.quantum_channels.append(channel)
        
    def set_student_implementation(self, implementation):
        """
        Set a custom student implementation for protocol methods.
        
        The implementation object should have methods like:
        - prepare_qubits_bb84(num_qubits)
        - measure_received_qubits(qubits)
        - reconcile_bases(other_bases)
        - estimate_error_rate(other_host, shared_indices)
        """
        self.student_implementation = implementation
        # Provide back-reference for bridges that need it
        try:
            if hasattr(self.student_implementation, 'host') and getattr(self.student_implementation, 'host', None) is None:
                self.student_implementation.host = self
        except Exception:
            pass
        # Validate now so protocol can proceed
        self.validate_student_implementation()
        print(f" Updated to student implementation: {type(implementation).__name__}")

    def prepare_qubit(self, basis: str, bit: int) -> qt.Qobj:
        """
        Prepare a qubit in the given basis and bit value.
        Students can override this for custom qubit preparation.
        """
        if self.student_implementation and hasattr(self.student_implementation, 'prepare_qubit'):
            return self.student_implementation.prepare_qubit(basis, bit)
        
        # Default implementation
        if basis == "Z":
            return qt.basis(2, bit)
        else:  # basis == "X"
            if bit == 0:
                return (qt.basis(2, 0) + qt.basis(2, 1)).unit()  # |+>
            else:
                return (qt.basis(2, 0) - qt.basis(2, 1)).unit()  # |->

    def measure_qubit(self, qubit: qt.Qobj, basis: str) -> int:
        """
        Measure a qubit in the given basis.
        Students can override this for custom measurement strategies.
        """
        if self.student_implementation and hasattr(self.student_implementation, 'measure_qubit'):
            return self.student_implementation.measure_qubit(qubit, basis)
        
        # Default implementation
        if basis == "Z":
            projector0 = qt.ket2dm(qt.basis(2, 0))
            projector1 = qt.ket2dm(qt.basis(2, 1))
        else:  # basis == "X"
            projector0 = qt.ket2dm((qt.basis(2, 0) + qt.basis(2, 1)).unit())
            projector1 = qt.ket2dm((qt.basis(2, 0) - qt.basis(2, 1)).unit())

        prob0 = qt.expect(projector0, qubit)
        return 0 if random.random() < prob0 else 1

    def bb84_send_qubits(self, num_qubits: int = None):
        """
        Send qubits using BB84 protocol.
        ABSOLUTELY REQUIRES student implementation - NO FALLBACKS!
        """
        if not self.check_student_implementation_required("BB84 Send Qubits"):
            return False
            
        # Prefer channel's configured bit count if not specified
        default_bits = 50
        try:
            chan = self.get_channel()
            if chan and getattr(chan, 'num_bits', None):
                default_bits = chan.num_bits
        except Exception:
            pass
        if self.student_implementation and hasattr(self.student_implementation, 'bb84_send_qubits'):
            # Reset protocol state for a fresh run
            self.basis_choices = []
            self.measurement_outcomes = []
            self.shared_bases_indices = []
            self._reconcile_sent = False
            
            # Ensure the student implementation has a reference to this host
            if not hasattr(self.student_implementation, 'host') or self.student_implementation.host is None:
                self.student_implementation.host = self
            
            print(f"🎓 {self.name}: Calling student BB84 implementation...")
            result = self.student_implementation.bb84_send_qubits(num_qubits or default_bits)
            print(f"🎓 {self.name}: Student implementation result: {result}")
            print(f"🎓 {self.name}: Host state after - bases: {len(self.basis_choices)}, outcomes: {len(self.measurement_outcomes)}")
            return result
        
        # NO FALLBACKS! Students must implement this themselves
        print(" BB84 Send Qubits BLOCKED - Student implementation required!")
        print(" VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION")
        print(" Students must implement bb84_send_qubits() method in the notebook")
        return False

    def process_received_qbit(self, qbit, from_channel: QuantumChannel):
        """
        Process a received qubit. ABSOLUTELY REQUIRES student implementation - NO FALLBACKS!
        """
        if not self.check_student_implementation_required("Process Received Qubit"):
            return False
            
        if self.student_implementation and hasattr(self.student_implementation, 'process_received_qbit'):
            # Ensure the student implementation has a reference to this host
            if not hasattr(self.student_implementation, 'host') or self.student_implementation.host is None:
                self.student_implementation.host = self
            
            return self.student_implementation.process_received_qbit(qbit, from_channel)
        
        # NO FALLBACKS! Students must implement this themselves
        print(" Process Received Qubit BLOCKED - Student implementation required!")
        print(" VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION")
        print(" Students must implement process_received_qbit() method in the notebook")
        return False

    def bb84_reconcile_bases(self, their_bases: List[str]):
        """
        Perform basis reconciliation. ABSOLUTELY REQUIRES student implementation - NO FALLBACKS!
        """
        if not self.check_student_implementation_required("BB84 Basis Reconciliation"):
            return False
            
        if self.student_implementation and hasattr(self.student_implementation, 'bb84_reconcile_bases'):
            return self.student_implementation.bb84_reconcile_bases(their_bases)
        
        # NO FALLBACKS! Students must implement this themselves
        print(" BB84 Basis Reconciliation BLOCKED - Student implementation required!")
        print(" VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION")
        print(" Students must implement bb84_reconcile_bases() method in the notebook")
        return False

    def bb84_estimate_error_rate(self, their_bits_sample: List[Tuple]):
        """
        Estimate error rate. ABSOLUTELY REQUIRES student implementation - NO FALLBACKS!
        """
        if not self.check_student_implementation_required("BB84 Error Rate Estimation"):
            return False
            
        if self.student_implementation and hasattr(self.student_implementation, 'bb84_estimate_error_rate'):
            return self.student_implementation.bb84_estimate_error_rate(their_bits_sample)
        
        # NO FALLBACKS! Students must implement this themselves
        print(" BB84 Error Rate Estimation BLOCKED - Student implementation required!")
        print(" VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION")
        print(" Students must implement bb84_estimate_error_rate() method in the notebook")
        return False

    def show_vibe_code_message(self):
        """Display the prominent vibe code message for students"""
        print("=" * 80)
        print(" VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION")
        print("=" * 80)
        print(" SIMULATION BLOCKED: Student implementation required!")
        print("")
        print(" TO UNLOCK THE SIMULATION:")
        print("1.  Open quantum_networking_interactive.ipynb")
        print("2.  Implement BB84 algorithms using the provided hints")
        print("3.  Connect your code to the simulation")
        print("4.  Run the simulation with YOUR quantum protocols!")
        print("")
        print(" HINTS AVAILABLE IN THE NOTEBOOK:")
        print("   • BB84 qubit generation and sending")
        print("   • Quantum measurement and basis reconciliation")
        print("   • Error rate estimation for eavesdropper detection")
        print("   • Complete implementation templates with examples")
        print("")
        print(" No hardcoded fallbacks - Pure student implementation required!")
        print("=" * 80)

    def get_learning_stats(self):
        """Get learning statistics for student progress tracking"""
        avg_error_rate = (sum(self.learning_stats['error_rates']) / 
                         len(self.learning_stats['error_rates'])) if self.learning_stats['error_rates'] else 0
        
        return {
            **self.learning_stats,
            'average_error_rate': avg_error_rate,
            'success_rate': (self.learning_stats['successful_protocols'] / 
                           max(1, len(self.learning_stats['error_rates']))) * 100
        }

    def reset_learning_stats(self):
        """Reset learning statistics"""
        self.learning_stats = {
            'qubits_sent': 0,
            'qubits_received': 0,
            'successful_protocols': 0,
            'error_rates': []
        }
        print(f" {self.name}: Learning statistics reset")

    # Override parent methods to support student implementations
    def receive_qubit(self, qbit, from_channel):
        """Override to add debug info"""
        print(f"🔬 {self.name}: Received qubit from {from_channel.name}")
        print(f"   Buffer size before: {self.qmemeory_buffer.qsize()}")
        super().receive_qubit(qbit, from_channel)
        print(f"   Buffer size after: {self.qmemeory_buffer.qsize()}")
    
    def forward(self):
        """Process quantum memory buffer"""
        while not self.qmemeory_buffer.empty():
            try:
                if self.protocol == "bb84" or self.entangled_channel:
                    qbit, from_channel = self.qmemeory_buffer.get()
                    self.process_received_qbit(qbit, from_channel)
                    # If we've received enough measurements for this session, trigger reconciliation once
                    try:
                        chan = self.get_channel()
                        expected = getattr(chan, 'num_bits', 0) or 0
                        if expected and not self._reconcile_sent and len(self.measurement_outcomes) >= expected:
                            self.send_bases_for_reconcile()
                            self._reconcile_sent = True
                    except Exception:
                        pass
                elif self.protocol == "entanglement_swapping":
                    print(f"ERROR: Host {self.name} received a qubit while in entanglement_swapping mode.")
                else:
                    print(f"Host {self.name} received qubit but has no protocol handler for '{self.protocol}'.")
            except Exception as e:
                traceback.print_exc()
                self.logger.error(f"Error processing received qubit: {e}")

    def send_qubit(self, qubit, channel: QuantumChannel):
        """Send a qubit through the quantum channel"""
        channel.transmit_qubit(qubit, self)
        self.qmemory = None

    def get_channel(self, to_host: QuantumNode = None):
        """Get quantum channel to specified host"""
        if to_host is None:
            return self.quantum_channels[0] if self.quantum_channels else None

        for chan in self.quantum_channels:
            if (chan.node_1 == self and chan.node_2 == to_host) or \
               (chan.node_2 == self and chan.node_1 == to_host):
                return chan
        return None

    def send_bases_for_reconcile(self):
        """Send basis choices for reconciliation"""
        # Log send
        try:
            self._send_update(
                SimulationEventType.INFO,
                data=dict(
                    type="qkd_reconcile_bases_sent",
                    host=self.name,
                    count=len(self.basis_choices),
                ),
            )
        except Exception:
            pass
        self.send_classical_data({
            'type': 'reconcile_bases',
            'data': self.basis_choices
        })

    def receive_classical_data(self, message):
        """Handle received classical data"""
        message_type = message.get("type")
        
        if self.protocol == "bb84" or self.entangled_channel:
            if message_type == "reconcile_bases":
                # Log receive
                try:
                    self._send_update(
                        SimulationEventType.INFO,
                        data=dict(
                            type="qkd_reconcile_bases_received",
                            host=self.name,
                            count=len(message.get("data", [])),
                        ),
                    )
                except Exception:
                    pass
                self.bb84_reconcile_bases(message["data"])
            elif message_type == "estimate_error_rate":
                try:
                    self._send_update(
                        SimulationEventType.INFO,
                        data=dict(
                            type="qkd_estimate_error_rate_received",
                            host=self.name,
                            sample_size=len(message.get("data", [])),
                        ),
                    )
                except Exception:
                    pass
                self.bb84_estimate_error_rate(message["data"])
            elif message_type == "complete":
                raw_key = self.bb84_extract_key()
                callback = getattr(self, 'qkd_completed_fn', None)
                if callback:
                    callback(raw_key)
                try:
                    self._send_update(
                        SimulationEventType.INFO,
                        data=dict(
                            type="qkd_complete_received",
                            host=self.name,
                            key_length=len(raw_key),
                        ),
                    )
                except Exception:
                    pass
            elif message_type == 'shared_bases_indices':
                try:
                    self._send_update(
                        SimulationEventType.INFO,
                        data=dict(
                            type="qkd_shared_bases_indices_received",
                            host=self.name,
                            count=len(message.get('data', [])),
                        ),
                    )
                except Exception:
                    pass
                
                # Use student implementation if available
                if self.student_implementation and hasattr(self.student_implementation, 'update_shared_bases_indices'):
                    self.student_implementation.update_shared_bases_indices(message['data'])
                else:
                    self.update_shared_bases_indices(message['data'])

    def update_shared_bases_indices(self, shared_base_indices):
        """Update shared bases indices and start error estimation"""
        channel = self.get_channel()
        self.shared_bases_indices = shared_base_indices
        # Log that shared indices were set
        try:
            self._send_update(
                SimulationEventType.INFO,
                data=dict(
                    type="qkd_shared_bases_indices_set",
                    host=self.name,
                    count=len(shared_base_indices),
                ),
            )
        except Exception:
            pass
        
        sample_size = random.randrange(2, channel.num_bits // 4)
        random_indices = random.sample(range(len(self.measurement_outcomes)), 
                                     min(sample_size, len(self.shared_bases_indices)))
        
        error_sample = [(self.measurement_outcomes[i], i) for i in random_indices]
        # Log that we are sending error estimation sample
        try:
            self._send_update(
                SimulationEventType.INFO,
                data=dict(
                    type="qkd_estimate_error_rate_sent",
                    host=self.name,
                    sample_size=len(error_sample),
                ),
            )
        except Exception:
            pass
        
        self.send_classical_data({
            'type': 'estimate_error_rate',
            'data': error_sample
        })

    def bb84_extract_key(self):
        """Extract the final shared key"""
        return [self.measurement_outcomes[i] for i in self.shared_bases_indices if 0 <= i < len(self.measurement_outcomes)]

    def perform_qkd(self):
        """Perform quantum key distribution"""
        if self.protocol == 'entanglement_swapping':
            # Entanglement-based protocols
            channel = self.get_channel()
            repeater = channel.get_other_node(self)
            if not isinstance(repeater, QuantumRepeater):
                print(f"ERROR: Host {self.name} is in 'entanglement_swapping' mode but no repeater found.")
                return
            target = repeater.get_other_node(self)
            self.request_entanglement(target)
            target.request_entanglement(self)
        else:
            # BB84 protocol
            self.bb84_send_qubits()

    def request_entanglement(self, target_host: 'InteractiveQuantumHost'):
        """Request entanglement with target host"""
        if self.protocol != "entanglement_swapping":
            print(f"ERROR: Host {self.name} is not in 'entanglement_swapping' mode.")
            return

        print(f"🔗 {self.name}: Requesting entanglement with {target_host.name}")
        
        channel = self.channel_exists(target_host)
        if not channel:
            print(f"ERROR: No channel found to {target_host.name}")
            return
            
        # Create Bell state
        bell_state = qt.bell_state("00")
        
        qubit_to_keep = qt.ptrace(bell_state, 0)
        qubit_to_send = qt.ptrace(bell_state, 1)

        self.entangled_qubit = qubit_to_keep
        self.entanglement_partner_address = target_host.name
        
        channel.transmit_qubit(qubit_to_send, self)

    def channel_exists(self, to_host: QuantumNode):
        """Check if channel exists to target host"""
        for chan in self.quantum_channels:
            if (chan.node_1 == self and chan.node_2 == to_host) or \
               (chan.node_2 == self and chan.node_1 == to_host):
                return chan
        return self.proxy_channel_exists(to_host)

    def proxy_channel_exists(self, to_host: QuantumNode):
        """Check for proxy channels through repeaters"""
        for chan in self.quantum_channels:
            if chan.node_1 == self:
                if isinstance(chan.node_2, QuantumRepeater) and chan.node_2.channel_exists(to_host):
                    return chan
            elif chan.node_2 == self:
                if isinstance(chan.node_1, QuantumRepeater) and chan.node_1.channel_exists(to_host):
                    return chan
        return None

    @property
    def is_eavesdropper(self):
        """Check if this host is configured as an eavesdropper"""
        return len(self.quantum_channels) == 2
    
    def on_qkd_completed(self, shared_key: List[int]):
        """Handle QKD completion and enable secure messaging"""
        if not hasattr(self, 'shared_key'):
            self.shared_key = shared_key
            print(f"🔑 {self.name}: QKD completed! Shared key established: {len(shared_key)} bits")
            print(f"   Key sample: {shared_key[:10]}..." if len(shared_key) > 10 else f"   Full key: {shared_key}")
            
            # Enable secure messaging capabilities
            self.enable_quantum_encryption()
    
    def enable_quantum_encryption(self):
        """Enable quantum encryption using the shared key"""
        if not hasattr(self, 'shared_key') or not self.shared_key:
            print(f"❌ {self.name}: No shared key available for encryption")
            return False
        
        print(f"🔐 {self.name}: Quantum encryption enabled with {len(self.shared_key)}-bit key")
        return True
    
    def quantum_encrypt_message(self, message: str) -> bytes:
        """Encrypt message using quantum-generated key"""
        if not hasattr(self, 'shared_key') or not self.shared_key:
            raise ValueError("No quantum key available for encryption")
        
        message_bytes = message.encode('utf-8')
        encrypted = bytearray()
        
        for i, byte in enumerate(message_bytes):
            # Use quantum key bits cyclically
            key_byte = 0
            for j in range(8):
                key_bit = self.shared_key[(i * 8 + j) % len(self.shared_key)]
                key_byte |= (key_bit << (7 - j))
            
            encrypted.append(byte ^ key_byte)
        
        print(f"🔒 {self.name}: Encrypted message using quantum key")
        return bytes(encrypted)
    
    def quantum_decrypt_message(self, encrypted_data: bytes) -> str:
        """Decrypt message using quantum-generated key"""
        if not hasattr(self, 'shared_key') or not self.shared_key:
            raise ValueError("No quantum key available for decryption")
        
        decrypted = bytearray()
        
        for i, byte in enumerate(encrypted_data):
            # Use quantum key bits cyclically
            key_byte = 0
            for j in range(8):
                key_bit = self.shared_key[(i * 8 + j) % len(self.shared_key)]
                key_byte |= (key_bit << (7 - j))
            
            decrypted.append(byte ^ key_byte)
        
        message = decrypted.decode('utf-8', errors='ignore')
        print(f"🔓 {self.name}: Decrypted message using quantum key")
        return message

    def __name__(self):
        return f"InteractiveQuantumHost - '{self.name}'"

    def __repr__(self):
        return self.__name__()


# Alias for backward compatibility
QuantumHost = InteractiveQuantumHost

