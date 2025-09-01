# 🔗 STUDENT BRIDGE IMPLEMENTATION
# This file contains the bridge code that connects student BB84 implementations to the simulation
# Students don't need to see or understand this - it's handled automatically

import random
import json

# Helper functions for quantum operations
try:
    import qutip as qt
except Exception:
    qt = None

def encode_qubit(bit, basis):
    """Return a qubit prepared in basis ('Z' or 'X') encoding the given bit."""
    b = 'Z' if basis in ('Z', 0) else 'X'
    if qt is not None:
        if b == 'Z':
            return qt.basis(2, bit)
        return (qt.basis(2, 0) + (1 if bit == 0 else -1) * qt.basis(2, 1)).unit()
    return (b, bit)

def measure_qubit(qubit, alice_basis, bob_basis):
    """Measure qubit in bob_basis ('Z'/'X' or 0/1)."""
    b = 'Z' if bob_basis in ('Z', 0) else 'X'
    if qt is not None and hasattr(qt, 'Qobj') and isinstance(qubit, qt.Qobj):
        if b == 'Z':
            proj0 = qt.ket2dm(qt.basis(2, 0))
        else:
            proj0 = qt.ket2dm((qt.basis(2, 0) + qt.basis(2, 1)).unit())
        p0 = qt.expect(proj0, qubit)
        return 0 if random.random() < p0 else 1
    if isinstance(qubit, tuple) and len(qubit) == 2:
        qb_basis, bit = qubit
        qb_b = 'Z' if qb_basis in ('Z', 0) else 'X'
        if qb_b == b:
            return bit
    return random.choice([0, 1])

class StudentImplementationBridge:
    """
    Bridge that connects your BB84 student implementation to the simulation.
    Uses Section 3 functions to drive the live simulator.
    """
    
    def __init__(self, student_alice=None, student_bob=None):
        # Handle case where simulation instantiates without parameters
        if student_alice is None or student_bob is None:
            # Use global instances if available
            global alice, bob
            self.student_alice = alice if alice is not None else self._create_dummy_host("Alice")
            self.student_bob = bob if bob is not None else self._create_dummy_host("Bob")
        else:
            self.student_alice = student_alice
            self.student_bob = student_bob
            
        self.host = None  # will be set when attached to a simulation host
        print("🔗 Bridge created! Your BB84 implementation is now connected to the simulation.")
    
    def _create_dummy_host(self, name):
        """Create a dummy host if student implementations aren't available"""
        class DummyHost:
            def __init__(self, name):
                self.name = name
                self.alice_bits = []
                self.alice_bases = []
                self.encoded_qubits = []
                self.basis_choices = []
                self.measurement_outcomes = []
            
            def bb84_send_qubits(self, num_qubits):
                print(f"⚠️ Using dummy implementation for {self.name}")
                return []
        
        return DummyHost(name)
    
    def bb84_send_qubits(self, num_qubits):
        """Send qubits via the simulator using Section 3 logic."""
        if self.host is None:
            print("⚠️ Bridge not attached to a simulation host")
            return False
        # Alice prepares qubits and bases using Section 3
        encoded_qubits = self.student_alice.bb84_send_qubits(num_qubits)
        # Record Alice's bases and bits on the simulation host so key extraction works
        self.host.basis_choices = list(self.student_alice.alice_bases)
        self.host.measurement_outcomes = list(self.student_alice.alice_bits)
        # Send through the actual quantum channel
        channel = self.host.get_channel()
        if channel is None:
            print(f"❌ ERROR: {self.host.name} has no quantum channel to send qubits.")
            return False
        for q in encoded_qubits:
            self.host.send_qubit(q, channel)
        return True
    
    def process_received_qbit(self, qbit, from_channel):
        """Measure a received qubit using Section 3 logic and store results on the host."""
        if self.host is None:
            return False
        # Bob chooses random basis (0=Z, 1=X)
        bob_basis = random.choice([0, 1])
        # Infer Alice basis from our simple string encoding
        if isinstance(qbit, str):
            alice_basis = 0 if qbit in ('|0⟩', '|1⟩') else 1
        else:
            # Default to random if unknown format
            alice_basis = random.choice([0, 1])
        outcome = measure_qubit(qbit, alice_basis, bob_basis)
        self.host.basis_choices.append(bob_basis)
        self.host.measurement_outcomes.append(outcome)
        return True
        
    def bb84_reconcile_bases(self, their_bases):
        """Find matching bases using the host's recorded bases and measurements."""
        shared_indices = [i for i, (a, b) in enumerate(zip(self.host.basis_choices, their_bases)) if a == b]
        self.host.shared_bases_indices = shared_indices
        # Notify peer
        self.host.send_classical_data({'type': 'shared_bases_indices', 'data': shared_indices})
        return shared_indices, [self.host.measurement_outcomes[i] for i in shared_indices if i < len(self.host.measurement_outcomes)]
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """Compute error rate from sampled indices and signal completion."""
        errors = 0
        comparisons = 0
        for bit, idx in their_bits_sample:
            if 0 <= idx < len(self.host.measurement_outcomes):
                comparisons += 1
                if self.host.measurement_outcomes[idx] != bit:
                    errors += 1
        error_rate = (errors / comparisons) if comparisons > 0 else 0.0
        self.host.learning_stats['error_rates'].append(error_rate)
        self.host.send_classical_data({'type': 'complete'})
        return error_rate

def create_student_bridge(alice_host, bob_host):
    """
    Simple function to create a bridge with student implementations.
    Students just need to call this function - no need to understand the bridge internals.
    """
    print("🌉 Creating student bridge...")
    bridge = StudentImplementationBridge(alice_host, bob_host)
    
    # Export implementation for simulation integration
    status = {
        "student_implementation_ready": True,
        "student_plugin_module": "student_impl_bridge",
        "student_plugin_class": "StudentImplementationBridge",
        "implementation_type": "NotebookIntegration",
        "methods_implemented": [
            "bb84_send_qubits",
            "process_received_qbit", 
            "bb84_reconcile_bases",
            "bb84_estimate_error_rate"
        ]
    }
    
    # Write status file for simulation
    with open("student_implementation_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
    
    print("✅ Bridge created and exported for simulation!")
    print("🎯 Your BB84 implementation is now ready for the quantum network!")
    
    return bridge

# Make alice and bob available for bridge creation
alice = None
bob = None

def set_student_implementations(alice_impl, bob_impl):
    """Set the student implementations for bridge creation"""
    global alice, bob
    alice = alice_impl
    bob = bob_impl
    print("✅ Student implementations registered for bridge creation")
    
    # Also create the bridge file that the simulation expects
    import json
    
    # Create a bridge file that the simulation can import
    bridge_code = '''# Auto-generated bridge for simulation
import sys
import os
sys.path.append(os.path.dirname(__file__))

from student_bridge_implementation import StudentImplementationBridge as BaseBridge, alice, bob

class StudentImplementationBridge:
    """Bridge wrapper that matches simulation expectations"""
    def __init__(self, host):
        self.host = host
        # Create the actual bridge with alice and bob
        self._bridge = BaseBridge(alice, bob)
        self._bridge.host = host
    
    def bb84_send_qubits(self, num_qubits):
        return self._bridge.bb84_send_qubits(num_qubits)
    
    def process_received_qbit(self, qbit, from_channel):
        return self._bridge.process_received_qbit(qbit, from_channel)
    
    def bb84_reconcile_bases(self, their_bases):
        return self._bridge.bb84_reconcile_bases(their_bases)
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        return self._bridge.bb84_estimate_error_rate(their_bits_sample)
'''
    
    with open("student_impl_bridge.py", "w", encoding="utf-8") as f:
        f.write(bridge_code)
    
    print("✅ Created student_impl_bridge.py for simulation integration")
