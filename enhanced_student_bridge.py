# enhanced_student_bridge.py
# ===================================
# Bridge for using StudentQuantumHost implementation from student_bb84_impl.py
# Preserves all features: qubit sending, receiving, basis reconciliation, error estimation
# Dynamic version - supports any host names

import random
import json

# Import student's actual BB84 implementation
from student_bb84_impl import StudentQuantumHost

# Helper functions for quantum operations (kept for compatibility)
def prepare_quantum_state(bit, basis):
    """Prepare a quantum state (used internally by fallback or testing)"""
    if basis == 0:  # Z-basis
        return '|0⟩' if bit == 0 else '|1⟩'
    else:  # X-basis
        return '|+⟩' if bit == 0 else '|-⟩'

def measure_quantum_state(quantum_state, measurement_basis):
    """Measure a quantum state in a given basis (used internally)"""
    if measurement_basis == 0:
        if quantum_state in ['|0⟩', '|1⟩']:
            return 0 if quantum_state == '|0⟩' else 1
        else:
            return random.randint(0, 1)
    else:
        if quantum_state in ['|+⟩', '|-⟩']:
            return 0 if quantum_state == '|+⟩' else 1
        else:
            return random.randint(0, 1)

# =================================================
# Enhanced bridge class using student's actual code - Dynamic
# =================================================
class EnhancedStudentImplementationBridge:
    """Directly uses StudentQuantumHost from student_bb84_impl.py with dynamic names"""
    
    def __init__(self, student_alice=None, student_bob=None, alice_name="Alice", bob_name="Bob"):
        # Store the actual names for dynamic logging
        self.alice_name = alice_name
        self.bob_name = bob_name
        
        if student_alice is None:
            self.student_alice = StudentQuantumHost(self.alice_name)
        else:
            self.student_alice = student_alice
            self.alice_name = student_alice.name  # Get actual name from student host
            
        if student_bob is None:
            self.student_bob = StudentQuantumHost(self.bob_name)
        else:
            self.student_bob = student_bob
            self.bob_name = student_bob.name  # Get actual name from student host
            
        self.host = None
        self.qkd_phase = "idle"
        self.bits_received = 0
        self.expected_bits = 0
    
    def bb84_send_qubits(self, num_qubits):
        """Send qubits using student's implementation directly"""
        if self.host is None:
            return False
            
        self.qkd_phase = "sending"
        self.expected_bits = num_qubits
        
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                   num_qubits=num_qubits, 
                                   protocol="BB84",
                                   message=f"STUDENT BB84: Starting with {num_qubits} qubits using student code",
                                   student_implementation="StudentQuantumHost")
        
        # Call student's method
        encoded_qubits = self.student_alice.bb84_send_qubits(num_qubits)
        
        # Store Alice's data on host
        self.host.basis_choices = list(self.student_alice.measurement_bases)
        self.host.measurement_outcomes = list(self.student_alice.random_bits)
        
        # Send through quantum channel
        channel = self.host.get_channel()
        if channel is None:
            return False
        
        for q in encoded_qubits:
            self.host.send_qubit(q, channel)
        
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.DATA_SENT, 
                                   qubits_sent=len(encoded_qubits),
                                   message=f"STUDENT BB84: Sent {len(encoded_qubits)} qubits")
        
        # Trigger reconciliation
        if self.host and hasattr(self.host, 'send_bases_for_reconcile'):
            self.host.send_bases_for_reconcile()
        
        return True
    
    def process_received_qbit(self, qbit, from_channel):
        """Measure received qubit using student's implementation"""
        if self.host is None:
            return False
            
        if self.qkd_phase == "idle":
            self.qkd_phase = "receiving"
            
        self.bits_received += 1
        result = self.student_bob.process_received_qbit(qbit, from_channel)
        
        self.host.basis_choices = list(self.student_bob.received_bases)
        self.host.measurement_outcomes = list(self.student_bob.measurement_outcomes)
        
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.DATA_RECEIVED,
                                   message=f"STUDENT {self.bob_name}: Received qubit {self.bits_received}/{self.expected_bits}",
                                   qubits_received=self.bits_received,
                                   total_expected=self.expected_bits)
        
        if self.bits_received >= self.expected_bits:
            self.qkd_phase = "ready_for_reconciliation"
        
        return result
    
    def bb84_reconcile_bases(self, their_bases):
        """Find matching bases using student's implementation"""
        if self.host is None:
            return False
        
        self.qkd_phase = "reconciling"
        
        shared_indices, shared_bits = self.student_bob.bb84_reconcile_bases(
            alice_bases=their_bases,
            bob_bases=self.student_bob.received_bases
        )
        
        self.host.shared_bases_indices = list(shared_indices)
        
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            efficiency = (len(shared_indices) / len(their_bases) * 100) if their_bases else 0
            self.host._send_update(SimulationEventType.INFO,
                                   message=f"STUDENT {self.bob_name}: Found {len(shared_indices)} matching bases ({efficiency:.1f}% efficiency)",
                                   shared_bases=len(shared_indices),
                                   efficiency=efficiency)
        
        self.host.send_classical_data({'type': 'shared_bases_indices', 'data': self.host.shared_bases_indices})
        return shared_indices, shared_bits
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """Compute error rate using student's implementation"""
        if self.host is None:
            return False
        
        self.qkd_phase = "error_checking"
        
        if not their_bits_sample:
            positions, reference_bits = [], []
        else:
            positions, reference_bits = zip(*their_bits_sample)
        
        error_rate = self.student_bob.bb84_estimate_error_rate(positions, reference_bits)
        
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO,
                                   message=f"STUDENT {self.bob_name}: Error rate {error_rate:.1%}",
                                   error_rate=error_rate)
        
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.SHARED_KEY_GENERATED,
                                   message="BB84 QKD protocol completed successfully using student code",
                                   error_rate=error_rate,
                                   shared_bases=len(self.host.shared_bases_indices))
        
        self.host.send_classical_data({'type': 'complete'})
        self.qkd_phase = "complete"
        
        return error_rate
    
    def update_shared_bases_indices(self, shared_base_indices):
        """Update shared bases indices - called by Alice"""
        if self.host is None:
            return False
        
        self.host.shared_bases_indices = shared_base_indices
        
        if self.host and hasattr(self.host, 'update_shared_bases_indices'):
            self.host.update_shared_bases_indices(shared_base_indices)
        
        return True

# ==========================================
# Dynamic factory function for easy setup
# ==========================================
def create_dynamic_bridge(host1_name, host2_name):
    """Create a bridge with custom host names"""
    student_host1 = StudentQuantumHost(host1_name)
    student_host2 = StudentQuantumHost(host2_name)
    
    bridge = EnhancedStudentImplementationBridge(
        student_alice=student_host1,
        student_bob=student_host2,
        alice_name=host1_name,
        bob_name=host2_name
    )
    return bridge

# ==========================================
# Wrapper to attach bridge to host - Dynamic
# ==========================================
class StudentImplementationBridge:
    """Wrapper that uses EnhancedStudentImplementationBridge with dynamic names"""
    
    def __init__(self, host, host1_name="Alice", host2_name="Bob"):
        self.host = host
        self._bridge = create_dynamic_bridge(host1_name, host2_name)
        self._bridge.host = host
    
    def set_host(self, host):
        self.host = host
        self._bridge.host = host
    
    def bb84_send_qubits(self, num_qubits):
        return self._bridge.bb84_send_qubits(num_qubits)
    
    def process_received_qbit(self, qbit, from_channel):
        return self._bridge.process_received_qbit(qbit, from_channel)
    
    def bb84_reconcile_bases(self, their_bases):
        return self._bridge.bb84_reconcile_bases(their_bases)
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        return self._bridge.bb84_estimate_error_rate(their_bits_sample)
