import random

class StudentImplementation:
    def __init__(self, host):
        self.host = host
        self.name = getattr(host, "name", "Student")
        self._rng = random.Random()

    def _rand_basis(self):
        return self._rng.choice(["Z","X"])

    def bb84_send_qubits(self, num_qubits: int):
        if hasattr(self.host, "reset_qkd_state"):
            self.host.reset_qkd_state()
        bits  = [self._rng.randint(0,1) for _ in range(num_qubits)]
        bases = [self._rand_basis() for _ in range(num_qubits)]
        self.host.basis_choices = bases
        chan = self.host.get_channel()
        if not chan:
            print(f"❌ {self.name}: No quantum channel"); return False
        for b, bas in zip(bits, bases):
            q = self.host.prepare_qubit(basis=bas, bit=b)
            self.host.send_qubit(q, chan)
        return True

    def process_received_qbit(self, qbit, from_channel):
        bas = self._rand_basis()
        bit = self.host.measure_qubit(qbit, bas)
        self.host.basis_choices.append(bas)
        self.host.measurement_outcomes.append(bit)
        return True

    def bb84_reconcile_bases(self, their_bases):
        ours = self.host.basis_choices
        n = min(len(ours), len(their_bases))
        shared = [i for i in range(n) if ours[i] == their_bases[i]]
        self.host.shared_bases_indices = shared
        self.host.send_classical_data({"type": "shared_bases_indices", "data": shared})
        return shared

    def bb84_estimate_error_rate(self, their_bits_sample):
        o = self.host.measurement_outcomes
        errors = comps = 0
        for their_bit, idx in their_bits_sample:
            if 0 <= idx < len(o):
                comps += 1
                if o[idx] != their_bit:
                    errors += 1
        self.host.send_classical_data({"type": "complete"})
        return (errors / comps) if comps else 0.0