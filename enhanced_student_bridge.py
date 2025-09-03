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

class EnhancedStudentImplementationBridge:
    """Enhanced bridge with proper QKD phase management and completion signals"""
    
    def __init__(self, student_alice=None, student_bob=None):
        # Handle case where simulation instantiates without parameters
        if student_alice is None or student_bob is None:
            # Use global instances if available
            try:
                global alice, bob
                self.student_alice = alice if 'alice' in globals() and alice is not None else self._create_dummy_host("Alice")
                self.student_bob = bob if 'bob' in globals() and bob is not None else self._create_dummy_host("Bob")
            except:
                self.student_alice = self._create_dummy_host("Alice")
                self.student_bob = self._create_dummy_host("Bob")
        else:
            self.student_alice = student_alice
            self.student_bob = student_bob
            
        self.host = None  # CRITICAL: Will be set when attached to simulation host
        self.qkd_phase = "idle"  # Track QKD phase: idle -> sending -> receiving -> reconciling -> error_checking -> complete
        self.bits_received = 0
        self.expected_bits = 50  # Default, will be updated from channel
        print("🔗 Enhanced Bridge created! BB84 implementation with completion signals enabled.")
    
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
        """Send qubits via the simulator using student implementation."""
        if self.host is None:
            print("⚠️ Bridge not attached to a simulation host")
            return False
            
        self.qkd_phase = "sending"
        self.expected_bits = num_qubits
        print(f"🚀 Starting BB84 protocol with {num_qubits} qubits")
        
        # Alice prepares qubits and bases using student implementation
        encoded_qubits = self.student_alice.bb84_send_qubits(num_qubits)
        
        # CRITICAL: Record Alice's bases and bits on the simulation host
        self.host.basis_choices = list(self.student_alice.alice_bases)
        self.host.measurement_outcomes = list(self.student_alice.alice_bits)
        
        # Send through the actual quantum channel
        channel = self.host.get_channel()
        if channel is None:
            print(f"❌ ERROR: {self.host.name} has no quantum channel to send qubits.")
            return False
        
        print(f"📤 Sending {len(encoded_qubits)} qubits through quantum channel...")
        for i, q in enumerate(encoded_qubits):
            self.host.send_qubit(q, channel)
            if i % 10 == 0:  # Progress indicator
                print(f"   Sent {i+1}/{len(encoded_qubits)} qubits")
        
        print(f"✅ All {len(encoded_qubits)} qubits sent successfully")
        return True
    
    def process_received_qbit(self, qbit, from_channel):
        """Measure a received qubit using student logic and store results on the host."""
        if self.host is None:
            return False
            
        if self.qkd_phase == "idle":
            self.qkd_phase = "receiving"
            print("📥 Started receiving qubits...")
            
        self.bits_received += 1
        
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
        
        # Progress indicator
        if self.bits_received % 10 == 0:
            print(f"   Received {self.bits_received}/{self.expected_bits} qubits")
        
        # Check if we've received all expected qubits
        if self.bits_received >= self.expected_bits:
            print(f"✅ Received all {self.bits_received} qubits, starting reconciliation...")
            self.qkd_phase = "ready_for_reconciliation"
            
        return True
        
    def bb84_reconcile_bases(self, their_bases):
        """Find matching bases and trigger error rate estimation."""
        if self.host is None:
            return False
            
        self.qkd_phase = "reconciling"
        print("🔄 Starting basis reconciliation...")
        
        # Find shared indices where bases match
        shared_indices = []
        for i, (my_basis, their_basis) in enumerate(zip(self.host.basis_choices, their_bases)):
            if my_basis == their_basis and i < len(self.host.measurement_outcomes):
                shared_indices.append(i)
        
        self.host.shared_bases_indices = shared_indices
        shared_bits = [self.host.measurement_outcomes[i] for i in shared_indices]
        
        print(f"✅ Reconciliation complete: {len(shared_indices)} shared bases out of {len(their_bases)} total")
        print(f"   Efficiency: {len(shared_indices)/len(their_bases)*100:.1f}%")
        
        # Notify peer about shared indices
        self.host.send_classical_data({
            'type': 'shared_bases_indices', 
            'data': shared_indices
        })
        
        return shared_indices, shared_bits
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """Compute error rate and CRITICAL: send completion signal."""
        if self.host is None:
            return False
            
        self.qkd_phase = "error_checking"
        print("🔍 Starting error rate estimation...")
        
        errors = 0
        comparisons = 0
        
        for bit, idx in their_bits_sample:
            if 0 <= idx < len(self.host.measurement_outcomes):
                comparisons += 1
                if self.host.measurement_outcomes[idx] != bit:
                    errors += 1
        
        error_rate = (errors / comparisons) if comparisons > 0 else 0.0
        
        print(f"📊 Error rate estimation complete:")
        print(f"   Sampled {comparisons} bits")
        print(f"   Found {errors} errors")
        print(f"   Error rate: {error_rate:.1%}")
        
        # Store learning stats
        if hasattr(self.host, 'learning_stats'):
            self.host.learning_stats['error_rates'].append(error_rate)
        
        # CRITICAL FIX: Send completion signal to notify adapters
        print("📡 Sending QKD completion signal...")
        self.host.send_classical_data({'type': 'complete'})
        
        # Update phase to complete
        self.qkd_phase = "complete"
        print("✅ BB84 PROTOCOL COMPLETE! 🎉")
        
        return error_rate

# Wrapper class that matches simulation expectations
class StudentImplementationBridge:
    """Bridge wrapper that connects to enhanced implementation"""
    def __init__(self, host):
        self.host = host
        # Create the enhanced bridge
        self._bridge = EnhancedStudentImplementationBridge()
        # CRITICAL FIX: Always set the host reference
        self._bridge.host = host
        print(f"🔗 Bridge attached to host: {host.name if host else 'Unknown'}")
    
    def bb84_send_qubits(self, num_qubits):
        return self._bridge.bb84_send_qubits(num_qubits)
    
    def process_received_qbit(self, qbit, from_channel):
        return self._bridge.process_received_qbit(qbit, from_channel)
    
    def bb84_reconcile_bases(self, their_bases):
        return self._bridge.bb84_reconcile_bases(their_bases)
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        return self._bridge.bb84_estimate_error_rate(their_bits_sample)
