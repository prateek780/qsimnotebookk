import random

def encode_qubit(bit, basis):
    """
    Encode a classical bit into a quantum state based on the chosen basis.
    
    Args:
        bit (int): 0 or 1 (classical bit)
        basis (int): 0 for computational basis, 1 for Hadamard basis
    
    Returns:
        str: Quantum state representation
    """
    if basis == 0:  # Computational basis
        return f"|{bit}⟩"
    else:  # Hadamard basis (|+⟩, |-⟩)
        if bit == 0:
            return "|+⟩"  # |+⟩ = (|0⟩ + |1⟩)/√2
        else:
            return "|-⟩"  # |-⟩ = (|0⟩ - |1⟩)/√2

def measure_qubit(qubit, alice_basis, bob_basis):
    """
    Measure a qubit in the specified basis.
    
    Args:
        qubit (str): Quantum state to measure
        alice_basis (int): Basis Alice used to encode (0 or 1)
        bob_basis (int): Basis Bob uses to measure (0 or 1)
    
    Returns:
        int: Measurement result (0 or 1)
    """
    if alice_basis == bob_basis:
        # Same basis - Bob gets Alice's original bit
        if alice_basis == 0:  # Computational basis
            if qubit == "|0⟩":
                return 0
            elif qubit == "|1⟩":
                return 1
        else:  # Hadamard basis
            if qubit == "|+⟩":
                return 0
            elif qubit == "|-⟩":
                return 1
    else:
        # Different basis - quantum uncertainty gives random result
        return random.choice([0, 1])
    
    # Fallback for unrecognized qubit states
    return random.choice([0, 1])
