import random
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

class StudentQuantumHost:
    """Your BB84 implementation"""
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.alice_bits = []
        self.alice_bases = []
        self.encoded_qubits = []
        self.basis_choices = []
        self.measurement_outcomes = []
        self.shared_key = []

    def bb84_send_qubits(self, num_qubits):
        """Alice sends qubits"""
        print(f"📤 {self.name}: Preparing {num_qubits} qubits for BB84...")
        self.alice_bits = [random.choice([0, 1]) for _ in range(num_qubits)]
        self.alice_bases = [random.choice([0, 1]) for _ in range(num_qubits)]
        self.basis_choices = self.alice_bases
        self.encoded_qubits = [encode_qubit(bit, basis) for bit, basis in zip(self.alice_bits, self.alice_bases)]
        print(f"✅ Prepared {len(self.encoded_qubits)} qubits")
        return self.encoded_qubits

class StudentImplementationBridge:
    """Bridge that connects your BB84 student implementation to the simulation."""

    def __init__(self, student_alice, student_bob):
        self.student_alice = student_alice
        self.student_bob = student_bob
        self.host = None
        print("🔗 Bridge created! Your BB84 implementation is now connected to the simulation.")

    def bb84_send_qubits(self, num_qubits):
        if self.host is None: 
            return False
        encoded_qubits = self.student_alice.bb84_send_qubits(num_qubits)
        self.host.basis_choices = list(self.student_alice.alice_bases)
        self.host.measurement_outcomes = list(self.student_alice.alice_bits)
        channel = self.host.get_channel()
        if channel is None: 
            return False
        for q in encoded_qubits:
            self.host.send_qubit(q, channel)
        return True

    def process_received_qbit(self, qbit, from_channel):
        if self.host is None: 
            return False
        bob_basis = random.choice([0, 1])
        alice_basis = 0 if isinstance(qbit, str) and qbit in ('|0⟩', '|1⟩') else 1
        outcome = measure_qubit(qbit, alice_basis, bob_basis)
        self.host.basis_choices.append(bob_basis)
        self.host.measurement_outcomes.append(outcome)
        return True

    def bb84_reconcile_bases(self, their_bases):
        shared_indices = [i for i, (a, b) in enumerate(zip(self.host.basis_choices, their_bases)) if a == b]
        self.host.shared_bases_indices = shared_indices
        self.host.send_classical_data({'type': 'shared_bases_indices', 'data': shared_indices})
        return shared_indices, [self.host.measurement_outcomes[i] for i in shared_indices if i < len(self.host.measurement_outcomes)]

    def bb84_estimate_error_rate(self, their_bits_sample):
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

# Create alice and bob instances
alice = StudentQuantumHost("Alice", "q_alice")
bob = StudentQuantumHost("Bob", "q_bob")

# Create the bridge
simulation_bridge = StudentImplementationBridge(alice, bob)

# Alias for the simulator
StudentImplementationBridge = StudentImplementationBridge
