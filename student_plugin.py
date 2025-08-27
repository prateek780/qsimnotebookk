import random
try:
    import qutip as qt  # Optional; used when available
except Exception:
    qt = None


class StudentPlugin:
    """
    Student BB84 implementation plugin.
    This class mirrors the "vibe-coded" notebook logic and is attached to
    InteractiveQuantumHost instances by the backend at simulation start.
    """

    def __init__(self, host):
        self.host = host

    # --- Optional overrides used by host if present ---
    def prepare_qubit(self, basis: str, bit: int):
        """Prepare a qubit. Use QuTiP when available, else return a lightweight marker."""
        if qt is not None:
            if basis == "Z":
                return qt.basis(2, bit)
            # X basis superpositions
            if bit == 0:
                return (qt.basis(2, 0) + qt.basis(2, 1)).unit()
            return (qt.basis(2, 0) - qt.basis(2, 1)).unit()
        # Fallback: lightweight tuple marker understood by our channel passthrough
        return (basis, bit)

    def measure_qubit(self, qubit, basis: str) -> int:
        """Measure in given basis. Uses QuTiP if available; else uses markers and randomness on mismatch."""
        if qt is not None and isinstance(qubit, qt.Qobj):
            # Projective measurement
            if basis == "Z":
                proj0 = qt.ket2dm(qt.basis(2, 0)); proj1 = qt.ket2dm(qt.basis(2, 1))
            else:  # X basis
                proj0 = qt.ket2dm((qt.basis(2, 0) + qt.basis(2, 1)).unit())
                proj1 = qt.ket2dm((qt.basis(2, 0) - qt.basis(2, 1)).unit())
            p0 = qt.expect(proj0, qubit)
            return 0 if random.random() < p0 else 1
        # Fallback for tuple markers
        if isinstance(qubit, tuple) and len(qubit) == 2:
            qb_basis, bit = qubit
            if qb_basis == basis:
                return bit
        return random.choice([0, 1])

    # --- Required protocol methods ---
    def bb84_send_qubits(self, num_qubits: int = 50):
        bits = [random.choice([0, 1]) for _ in range(num_qubits)]
        bases = [random.choice(["Z", "X"]) for _ in range(num_qubits)]
        self.host.basis_choices = bases

        channel = self.host.get_channel()
        if channel is None:
            print(f"ERROR: {self.host.name} has no quantum channel to send qubits.")
            return False

        for bit, basis in zip(bits, bases):
            q = self.prepare_qubit(basis, bit)
            self.host.send_qubit(q, channel)

        self.host.learning_stats['qubits_sent'] += num_qubits
        return True

    def process_received_qbit(self, qbit, from_channel):
        basis = random.choice(["Z", "X"])  # Bob chooses basis
        outcome = self.measure_qubit(qbit, basis)
        self.host.basis_choices.append(basis)
        self.host.measurement_outcomes.append(outcome)
        self.host.learning_stats['qubits_received'] += 1
        return True

    def bb84_reconcile_bases(self, their_bases):
        shared = [i for i, (a, b) in enumerate(zip(self.host.basis_choices, their_bases)) if a == b]
        self.host.shared_bases_indices = shared
        # Notify peer to proceed with error estimation
        self.host.send_classical_data({'type': 'shared_bases_indices', 'data': shared})
        # Safely return bits only for indices we actually have
        bits_available = [self.host.measurement_outcomes[i] for i in shared if i < len(self.host.measurement_outcomes)]
        return shared, bits_available

    def bb84_estimate_error_rate(self, their_bits_sample):
        # their_bits_sample: list of tuples (bit, idx)
        errors = 0
        comparisons = 0
        for bit, idx in their_bits_sample:
            if 0 <= idx < len(self.host.measurement_outcomes):
                comparisons += 1
                if self.host.measurement_outcomes[idx] != bit:
                    errors += 1
        error_rate = (errors / comparisons) if comparisons > 0 else 0.0
        self.host.learning_stats['error_rates'].append(error_rate)
        # Signal completion
        self.host.send_classical_data({'type': 'complete'})
        return error_rate


