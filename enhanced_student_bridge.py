import random
import json

# Helper functions for quantum operations
try:
    import qutip as qt
except Exception:
    qt = None

# Import student's BB84 implementation functions from notebook
def prepare_quantum_state(bit, basis):
    """
    Prepare a quantum state for BB84 protocol
    
    Args:
        bit: 0 or 1 (the classical bit to encode)
        basis: 0 (Z-basis) or 1 (X-basis)
    
    Returns:
        String representation of the quantum state
    """
    if basis == 0:  # Z-basis (computational basis)
        if bit == 0:
            return '|0⟩'  # |0⟩ state
        else:
            return '|1⟩'  # |1⟩ state
    else:  # X-basis (Hadamard basis)
        if bit == 0:
            return '|+⟩'  # |+⟩ = (|0⟩ + |1⟩)/√2
        else:
            return '|-⟩'  # |-⟩ = (|0⟩ - |1⟩)/√2

def measure_quantum_state(quantum_state, measurement_basis):
    """
    Measure a quantum state in a given basis.

    Args:
        quantum_state: one of '|0⟩', '|1⟩', '|+⟩', '|-⟩'
        measurement_basis: 0 = Z, 1 = X

    Returns:
        0 or 1
    """
    if measurement_basis == 0:  # Z-basis measurement
        if quantum_state in ['|0⟩', '|1⟩']:
            return 0 if quantum_state == '|0⟩' else 1
        else:
            # Measuring X states in Z basis is random
            return random.randint(0, 1)
    else:  # X-basis measurement
        if quantum_state in ['|+⟩', '|-⟩']:
            return 0 if quantum_state == '|+⟩' else 1
        else:
            # Measuring Z states in X basis is random
            return random.randint(0, 1)

# SIMPLIFIED: Direct import of student's code from notebook
def get_student_quantum_host():
    """
    Get the student's StudentQuantumHost class from the notebook
    This is much simpler and more reliable than complex import logic
    """
    try:
        # Try to get from globals (notebook execution context)
        import sys
        current_frame = sys._getframe(1)
        global_vars = current_frame.f_globals
        
        if 'StudentQuantumHost' in global_vars:
            print("✅ Found StudentQuantumHost in notebook globals!")
            return global_vars['StudentQuantumHost']
        
        # Try to get from builtins (notebook scope)
        if hasattr(__builtins__, '__dict__') and 'StudentQuantumHost' in __builtins__.__dict__:
            print("✅ Found StudentQuantumHost in builtins!")
            return __builtins__.__dict__['StudentQuantumHost']
        
        print("❌ StudentQuantumHost not found in globals")
        return None
        
    except Exception as e:
        print(f"❌ Error getting StudentQuantumHost: {e}")
        return None

# Get the student's class
StudentQuantumHost = get_student_quantum_host()

# If not found, create a simple fallback that matches the student's interface
if StudentQuantumHost is None:
    print("⚠️ Creating fallback StudentQuantumHost (student's class not found)")
    
    class StudentQuantumHost:
        """Fallback that matches student's interface exactly"""
        
        def __init__(self, name):
            self.name = name
            # Match student's exact data structure names
            self.alice_bits = []
            self.alice_bases = []
            self.encoded_qubits = []
            self.basis_choices = []
            self.measurement_outcomes = []
            self.shared_bases_indices = []
            self.shared_bits = []
            
            print(f"{self.name} initialized! Ready for BB84 protocol!")
        
        def bb84_send_qubits(self, num_qubits):
            print(f"{self.name} preparing {num_qubits} qubits for BB84...")
            
            self.alice_bits = []
            self.alice_bases = []
            self.encoded_qubits = []
            
            for i in range(num_qubits):
                bit = random.randint(0, 1)
                basis = random.randint(0, 1)
                self.alice_bits.append(bit)
                self.alice_bases.append(basis)
                
                qubit = prepare_quantum_state(bit, basis)
                self.encoded_qubits.append(qubit)
            
            print(f"{self.name} prepared {len(self.encoded_qubits)} qubits")
            print(f"   Bits: {self.alice_bits[:10]}{'...' if len(self.alice_bits) > 10 else ''}")
            print(f"   Bases: {self.alice_bases[:10]}{'...' if len(self.alice_bases) > 10 else ''}")
            
            return self.encoded_qubits
        
        def process_received_qbit(self, qbit, from_channel):
            measurement_basis = random.randint(0, 1)
            self.basis_choices.append(measurement_basis)
            
            measurement_result = measure_quantum_state(qbit, measurement_basis)
            self.measurement_outcomes.append(measurement_result)
            
            return True
        
        def bb84_reconcile_bases(self, their_bases):
            print(f"{self.name} reconciling bases...")
            
            shared_indices = []
            shared_bits = []
            
            for i, (my_basis, their_basis) in enumerate(zip(self.basis_choices, their_bases)):
                if my_basis == their_basis and i < len(self.measurement_outcomes):
                    shared_indices.append(i)
                    shared_bits.append(self.measurement_outcomes[i])
            
            self.shared_bases_indices = shared_indices
            self.shared_bits = shared_bits
            
            print(f"{self.name} found {len(shared_indices)} matching bases out of {len(their_bases)}")
            print(f"   Efficiency: {len(shared_indices)/len(their_bases)*100:.1f}%")
            
            return shared_indices, shared_bits
        
        def bb84_estimate_error_rate(self, their_bits_sample):
            print(f"{self.name} estimating error rate...")
            
            errors = 0
            comparisons = 0
            
            for bit, index in their_bits_sample:
                if 0 <= index < len(self.measurement_outcomes):
                    comparisons += 1
                    if self.measurement_outcomes[index] != bit:
                        errors += 1
            
            error_rate = (errors / comparisons) if comparisons > 0 else 0.0
            
            print(f"{self.name} error rate: {error_rate:.1%} ({errors}/{comparisons} errors)")
            
            return error_rate
else:
    print("✅ Successfully using student's actual StudentQuantumHost from notebook!")
    print("🎯 Using student's vibe code - no fallback needed!")

class EnhancedStudentImplementationBridge:
    """SIMPLIFIED: Direct use of student's StudentQuantumHost class"""
    
    def __init__(self, student_alice=None, student_bob=None):
        # SIMPLIFIED: Direct instantiation using the imported StudentQuantumHost
        if student_alice is None:
            print("Creating Alice using StudentQuantumHost...")
            self.student_alice = StudentQuantumHost("Alice")
        else:
            self.student_alice = student_alice
            
        if student_bob is None:
            print("Creating Bob using StudentQuantumHost...")
            self.student_bob = StudentQuantumHost("Bob")
        else:
            self.student_bob = student_bob
            
        self.host = None  # Will be set when attached to simulation host
        self.qkd_phase = "idle"
        self.bits_received = 0
        self.expected_bits = 0
        
        print("✅ Enhanced Bridge created using StudentQuantumHost!")
        print(f"   Alice type: {type(self.student_alice).__name__}")
        print(f"   Bob type: {type(self.student_bob).__name__}")
        print("🎯 Using student's vibe code directly!")
    
    def bb84_send_qubits(self, num_qubits):
        """Send qubits using student's implementation directly"""
        if self.host is None:
            print("Bridge not attached to a simulation host")
            return False
            
        self.qkd_phase = "sending"
        self.expected_bits = num_qubits
        print(f"Starting BB84 protocol with {num_qubits} qubits")
        
        # Send UI event for BB84 start
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                 num_qubits=num_qubits, 
                                 protocol="BB84",
                                 message=f"STUDENT BB84: Starting with {num_qubits} qubits using your vibe code!",
                                 student_implementation="StudentQuantumHost")
        
        # DIRECT CALL to student's method
        encoded_qubits = self.student_alice.bb84_send_qubits(num_qubits)
        
        # Store Alice's data on simulation host
        self.host.basis_choices = list(self.student_alice.alice_bases)
        self.host.measurement_outcomes = list(self.student_alice.alice_bits)
        
        # Send through quantum channel
        channel = self.host.get_channel()
        if channel is None:
            print(f"ERROR: {self.host.name} has no quantum channel")
            return False
        
        print(f"Sending {len(encoded_qubits)} qubits through quantum channel...")
        
        # Send qubits with progress tracking
        for i, q in enumerate(encoded_qubits):
            self.host.send_qubit(q, channel)
            if i % 10 == 0:
                print(f"   Sent {i+1}/{len(encoded_qubits)} qubits")
        
        print(f"All {len(encoded_qubits)} qubits sent successfully")
        
        # Send UI event for qubit transmission
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.DATA_SENT, 
                                 qubits_sent=len(encoded_qubits),
                                 message=f"STUDENT BB84: Sent {len(encoded_qubits)} qubits using your bb84_send_qubits() method!")
        
        # Trigger reconciliation
        print(f"Alice: Triggering reconciliation...")
        if self.host and hasattr(self.host, 'send_bases_for_reconcile'):
            self.host.send_bases_for_reconcile()
            print(f"Alice: Reconciliation bases sent")
        
        return True
    
    def process_received_qbit(self, qbit, from_channel):
        """Measure received qubit using student's implementation"""
        if self.host is None:
            return False
            
        if self.qkd_phase == "idle":
            self.qkd_phase = "receiving"
            print("Started receiving qubits...")
            
        self.bits_received += 1
        
        # DIRECT CALL to student's method
        result = self.student_bob.process_received_qbit(qbit, from_channel)
        
        # Update host's state with Bob's results
        self.host.basis_choices = list(self.student_bob.basis_choices)
        self.host.measurement_outcomes = list(self.student_bob.measurement_outcomes)
        
        # Send UI event for qubit reception
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.DATA_RECEIVED,
                                 message=f"STUDENT BOB: Received qubit {self.bits_received}/{self.expected_bits} using your process_received_qbit() method!",
                                 qubits_received=self.bits_received,
                                 total_expected=self.expected_bits)
        
        # Progress indicator
        if self.bits_received % 10 == 0:
            print(f"   Received {self.bits_received}/{self.expected_bits} qubits")
        
        # Check completion
        if self.bits_received >= self.expected_bits:
            print(f"Received all {self.bits_received} qubits, ready for reconciliation...")
            self.qkd_phase = "ready_for_reconciliation"
        
        return result
        
    def bb84_reconcile_bases(self, their_bases):
        """Find matching bases using student's implementation"""
        if self.host is None:
            return False
            
        self.qkd_phase = "reconciling"
        print("Starting basis reconciliation...")
        
        # DIRECT CALL to student's method
        shared_indices, shared_bits = self.student_bob.bb84_reconcile_bases(their_bases)
        
        # Update host's state
        self.host.shared_bases_indices = list(shared_indices)
        
        # Send UI event for reconciliation
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            efficiency = (len(shared_indices) / len(their_bases) * 100) if their_bases else 0
            self.host._send_update(SimulationEventType.INFO, 
                                 message=f"STUDENT BOB: Found {len(shared_indices)} matching bases ({efficiency:.1f}% efficiency) using your bb84_reconcile_bases() method!",
                                 shared_bases=len(shared_indices),
                                 efficiency=efficiency)
        
        # Notify peer
        self.host.send_classical_data({
            'type': 'shared_bases_indices', 
            'data': self.host.shared_bases_indices
        })
        
        return shared_indices, shared_bits
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """Compute error rate using student's implementation"""
        if self.host is None:
            return False
            
        self.qkd_phase = "error_checking"
        print("Starting error rate estimation...")
        
        # DIRECT CALL to student's method
        error_rate = self.student_bob.bb84_estimate_error_rate(their_bits_sample)
        
        print(f"Student Bob error rate: {error_rate:.1%}")
        
        # Send UI event for error estimation
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                 message=f"STUDENT BOB: Error rate {error_rate:.1%} using your bb84_estimate_error_rate() method!",
                                 error_rate=error_rate)
        
        # Send completion signal
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.SHARED_KEY_GENERATED, 
                                 message="BB84 QKD protocol completed successfully using student's vibe code!",
                                 error_rate=error_rate,
                                 shared_bases=len(self.host.shared_bases_indices))
        
        self.host.send_classical_data({'type': 'complete'})
        self.qkd_phase = "complete"
        
        print("BB84 PROTOCOL COMPLETE using student's implementation!")
        
        return error_rate
    
    def update_shared_bases_indices(self, shared_base_indices):
        """Update shared bases indices - called by Alice"""
        if self.host is None:
            return False
            
        print(f"Alice: Received {len(shared_base_indices)} shared bases indices from Bob")
        self.host.shared_bases_indices = shared_base_indices
        
        # Trigger error estimation
        if self.host and hasattr(self.host, 'update_shared_bases_indices'):
            self.host.update_shared_bases_indices(shared_base_indices)
        
        return True

# SIMPLIFIED: Wrapper class that uses student's code directly
class StudentImplementationBridge:
    """Bridge wrapper that uses student's StudentQuantumHost directly"""
    def __init__(self, host):
        self.host = host
        # Create enhanced bridge with student's code
        self._bridge = EnhancedStudentImplementationBridge()
        self._bridge.host = host
        print(f"✅ Bridge created using student's vibe code for host: {host.name if host else 'Unknown'}")
    
    def set_host(self, host):
        """Set the host reference after creation"""
        self.host = host
        self._bridge.host = host
        print(f"Bridge host updated: {host.name if host else 'Unknown'}")
    
    def bb84_send_qubits(self, num_qubits):
        return self._bridge.bb84_send_qubits(num_qubits)
    
    def process_received_qbit(self, qbit, from_channel):
        return self._bridge.process_received_qbit(qbit, from_channel)
    
    def bb84_reconcile_bases(self, their_bases):
        return self._bridge.bb84_reconcile_bases(their_bases)
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        return self._bridge.bb84_estimate_error_rate(their_bits_sample)