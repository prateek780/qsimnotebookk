#!/usr/bin/env python3
"""
Introduction to Quantum Networking with BB84 Protocol
====================================================

This script provides a comprehensive implementation of quantum networking concepts
and the BB84 quantum key distribution protocol. It's designed to be completed
in 3-4 days and includes interactive elements and GitHub Copilot integration.

Learning Objectives:
- Understand quantum networking fundamentals
- Implement BB84 quantum key distribution protocol
- Explore AI-assisted quantum coding with GitHub Copilot
- Build interactive quantum simulations

Author: AI Assistant
Timeline: 3-4 days
Prerequisites: Basic Python, linear algebra concepts
"""

# ============================================================================
# SECTION 1: SETUP AND DEPENDENCIES
# ============================================================================

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import qutip as qt
from qutip import *
import warnings
import time
from typing import List, Tuple, Dict, Any

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('default')
sns.set_palette("husl")

print("🚀 Quantum Networking with BB84 Protocol")
print("=" * 50)
print("✅ All libraries imported successfully!")
print(f"Qutip version: {qt.__version__}")
print(f"NumPy version: {np.__version__}")

# ============================================================================
# SECTION 2: QUANTUM NETWORKING FUNDAMENTALS
# ============================================================================

def visualize_qubit_state(alpha: float, beta: float) -> None:
    """
    Visualize a qubit state |ψ⟩ = α|0⟩ + β|1⟩
    
    Args:
        alpha: Amplitude of |0⟩ state
        beta: Amplitude of |1⟩ state
    """
    
    # Normalize the state
    norm = np.sqrt(alpha**2 + beta**2)
    alpha_norm = alpha / norm
    beta_norm = beta / norm
    
    # Create Bloch sphere visualization
    fig = plt.figure(figsize=(15, 5))
    
    # Bloch sphere
    ax1 = fig.add_subplot(131, projection='3d')
    b = qt.Bloch(axes=ax1)
    state = alpha_norm * qt.basis(2, 0) + beta_norm * qt.basis(2, 1)
    b.add_states(state)
    b.render()
    ax1.set_title(f'Bloch Sphere: |ψ⟩ = {alpha_norm:.2f}|0⟩ + {beta_norm:.2f}|1⟩')
    
    # State vector
    ax2 = fig.add_subplot(132)
    states = ['|0⟩', '|1⟩']
    amplitudes = [abs(alpha_norm), abs(beta_norm)]
    phases = [np.angle(alpha_norm), np.angle(beta_norm)]
    
    bars = ax2.bar(states, amplitudes, color=['skyblue', 'lightcoral'])
    ax2.set_ylabel('Amplitude')
    ax2.set_title('State Amplitudes')
    
    # Add phase information
    for i, (bar, phase) in enumerate(zip(bars, phases)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'φ={phase:.2f}', ha='center', va='bottom')
    
    # Phase plot
    ax3 = fig.add_subplot(133, projection='polar')
    angles = [0, np.angle(alpha_norm), np.angle(beta_norm)]
    radii = [0, abs(alpha_norm), abs(beta_norm)]
    ax3.scatter(angles[1:], radii[1:], c=['skyblue', 'lightcoral'], s=100)
    ax3.set_title('Phase Representation')
    
    plt.tight_layout()
    plt.show()
    
    # Print state information
    print(f"\n📊 State Information:")
    print(f"Normalized state: |ψ⟩ = {alpha_norm:.3f}|0⟩ + {beta_norm:.3f}|1⟩")
    print(f"Probability of |0⟩: {abs(alpha_norm)**2:.3f}")
    print(f"Probability of |1⟩: {abs(beta_norm)**2:.3f}")
    print(f"Phase of |0⟩: {np.angle(alpha_norm):.3f} radians")
    print(f"Phase of |1⟩: {np.angle(beta_norm):.3f} radians")

def demonstrate_quantum_superposition():
    """Demonstrate quantum superposition with different qubit states"""
    print("\n🔬 Quantum Superposition Demonstration")
    print("=" * 40)
    
    # Example 1: Equal superposition |+⟩
    print("\n1. Equal Superposition |+⟩ = (|0⟩ + |1⟩)/√2")
    visualize_qubit_state(1.0, 1.0)
    
    # Example 2: Unequal superposition
    print("\n2. Unequal Superposition |ψ⟩ = 0.8|0⟩ + 0.6|1⟩")
    visualize_qubit_state(0.8, 0.6)
    
    # Example 3: Phase difference
    print("\n3. Phase Difference |ψ⟩ = |0⟩ + i|1⟩")
    visualize_qubit_state(1.0, 1j)

# ============================================================================
# SECTION 3: BB84 PROTOCOL IMPLEMENTATION
# ============================================================================

class BB84Protocol:
    """
    Implementation of the BB84 quantum key distribution protocol.
    
    BB84 allows two parties (Alice and Bob) to establish a shared secret key
    while detecting any eavesdropping attempts.
    """
    
    def __init__(self, key_length: int = 100):
        """
        Initialize BB84 protocol.
        
        Args:
            key_length: Length of the key to generate
        """
        self.key_length = key_length
        self.alice_bits = None
        self.alice_bases = None
        self.bob_bases = None
        self.bob_measurements = None
        self.shared_key = None
        self.eavesdropper_present = False
        
    def alice_prepare_qubits(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Alice generates random bits and bases, then prepares qubits.
        
        Returns:
            Tuple of (bits, bases)
        """
        # Generate random bits (0 or 1)
        self.alice_bits = np.random.randint(2, size=self.key_length)
        # Generate random bases (0 for computational, 1 for Hadamard)
        self.alice_bases = np.random.randint(2, size=self.key_length)
        
        print(f"🔐 Alice generated {self.key_length} random bits and bases")
        print(f"Bits: {self.alice_bits[:10]}... (showing first 10)")
        print(f"Bases: {self.alice_bases[:10]}... (showing first 10)")
        
        return self.alice_bits, self.alice_bases
    
    def encode_qubit(self, bit: int, base: int) -> qt.Qobj:
        """
        Encode a bit into a qubit using the specified base.
        
        Args:
            bit: Bit value (0 or 1)
            base: Basis choice (0 for computational, 1 for Hadamard)
            
        Returns:
            Quantum state representing the encoded bit
        """
        if base == 0:  # Computational basis
            if bit == 0:
                return qt.basis(2, 0)  # |0⟩
            else:
                return qt.basis(2, 1)  # |1⟩
        else:  # Hadamard basis
            if bit == 0:
                return (qt.basis(2, 0) + qt.basis(2, 1)) / np.sqrt(2)  # |+⟩
            else:
                return (qt.basis(2, 0) - qt.basis(2, 1)) / np.sqrt(2)  # |−⟩
    
    def bob_measure_qubits(self, qubits: List[qt.Qobj], 
                          eavesdropper_interference: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        """
        Bob measures qubits in random bases.
        
        Args:
            qubits: List of quantum states to measure
            eavesdropper_interference: Whether to simulate eavesdropper interference
            
        Returns:
            Tuple of (bob_bases, bob_measurements)
        """
        self.bob_bases = np.random.randint(2, size=self.key_length)
        self.bob_measurements = np.zeros(self.key_length, dtype=int)
        
        # Simulate eavesdropper interference if enabled
        if eavesdropper_interference:
            self.eavesdropper_present = True
            print("👁️ Eavesdropper (Eve) is intercepting the communication!")
            
            # Eve measures in random bases, introducing errors
            for i in range(self.key_length):
                eve_basis = np.random.randint(2)
                if eve_basis != self.alice_bases[i]:
                    # Eve's measurement disturbs the state
                    qubits[i] = self.encode_qubit(np.random.randint(2), eve_basis)
        
        # Bob measures each qubit
        for i in range(self.key_length):
            if self.bob_bases[i] == 0:  # Computational basis
                # Measure in computational basis
                result = qt.mesolve(qt.sigmaz(), qubits[i], [], [qt.sigmaz()])
                expectation = result.expect[0][0]
                self.bob_measurements[i] = 0 if expectation > 0 else 1
            else:  # Hadamard basis
                # Measure in Hadamard basis
                hadamard = qt.hadamard_transform()
                transformed_state = hadamard * qubits[i]
                result = qt.mesolve(qt.sigmaz(), transformed_state, [], [qt.sigmaz()])
                expectation = result.expect[0][0]
                self.bob_measurements[i] = 0 if expectation > 0 else 1
        
        print(f"🔍 Bob measured qubits in random bases")
        print(f"Bob's bases: {self.bob_bases[:10]}... (showing first 10)")
        print(f"Bob's measurements: {self.bob_measurements[:10]}... (showing first 10)")
        
        return self.bob_bases, self.bob_measurements
    
    def establish_shared_key(self) -> Tuple[np.ndarray, float, bool]:
        """
        Establish shared key by comparing bases and keeping matching measurements.
        
        Returns:
            Tuple of (shared_key, error_rate, eavesdropper_detected)
        """
        # Find positions where bases match
        matching_bases = (self.alice_bases == self.bob_bases)
        matching_indices = np.where(matching_bases)[0]
        
        # Extract shared key
        alice_shared_bits = self.alice_bits[matching_indices]
        bob_shared_bits = self.bob_measurements[matching_indices]
        
        # Check for errors (should be 0 if no eavesdropper)
        errors = np.sum(alice_shared_bits != bob_shared_bits)
        error_rate = errors / len(alice_shared_bits) if len(alice_shared_bits) > 0 else 0
        
        # Use Alice's bits as the final key (they should match Bob's if no eavesdropper)
        self.shared_key = alice_shared_bits
        
        print(f"\n🔑 Shared Key Established!")
        print(f"Matching bases: {len(matching_indices)}/{self.key_length} ({len(matching_indices)/self.key_length*100:.1f}%)")
        print(f"Shared key length: {len(self.shared_key)}")
        print(f"Errors detected: {errors}")
        print(f"Error rate: {error_rate:.3f}")
        
        if error_rate > 0.1:  # Threshold for eavesdropper detection
            print("🚨 WARNING: High error rate detected! Possible eavesdropper present.")
            self.eavesdropper_present = True
        else:
            print("✅ Low error rate - communication appears secure!")
        
        return self.shared_key, error_rate, self.eavesdropper_present
    
    def run_protocol(self, eavesdropper_interference: bool = False) -> Dict[str, Any]:
        """
        Run the complete BB84 protocol.
        
        Args:
            eavesdropper_interference: Whether to simulate eavesdropper interference
            
        Returns:
            Dictionary containing protocol results
        """
        print("🚀 Starting BB84 Protocol Simulation...")
        print("=" * 50)
        
        # Step 1: Alice prepares qubits
        alice_bits, alice_bases = self.alice_prepare_qubits()
        
        # Step 2: Encode qubits
        qubits = [self.encode_qubit(bit, base) for bit, base in zip(alice_bits, alice_bases)]
        print(f"\n📡 Alice encoded {len(qubits)} qubits and sent them to Bob")
        
        # Step 3: Bob measures qubits
        bob_bases, bob_measurements = self.bob_measure_qubits(qubits, eavesdropper_interference)
        
        # Step 4: Establish shared key
        shared_key, error_rate, eavesdropper_detected = self.establish_shared_key()
        
        print("\n" + "=" * 50)
        print("🏁 BB84 Protocol Complete!")
        
        return {
            'shared_key': shared_key,
            'error_rate': error_rate,
            'eavesdropper_detected': eavesdropper_detected,
            'matching_bases': np.sum(alice_bases == bob_bases),
            'total_qubits': self.key_length
        }

# ============================================================================
# SECTION 4: INTERACTIVE BB84 SIMULATION
# ============================================================================

def run_multiple_bb84_simulations(key_length: int, eavesdropper_present: bool, 
                                 num_runs: int) -> List[Dict[str, Any]]:
    """
    Run multiple BB84 simulations with specified parameters.
    
    Args:
        key_length: Length of key to generate
        eavesdropper_present: Whether to include eavesdropper interference
        num_runs: Number of simulation runs
        
    Returns:
        List of simulation results
    """
    results = []
    error_rates = []
    key_lengths = []
    eavesdropper_detected = []
    
    print(f"🔄 Running {num_runs} BB84 simulations...")
    print(f"Key length: {key_length}, Eavesdropper: {eavesdropper_present}")
    print("=" * 60)
    
    for run in range(num_runs):
        bb84 = BB84Protocol(key_length=key_length)
        result = bb84.run_protocol(eavesdropper_interference=eavesdropper_present)
        
        results.append(result)
        error_rates.append(result['error_rate'])
        key_lengths.append(result['matching_bases'])
        eavesdropper_detected.append(result['eavesdropper_detected'])
        
        if run < 3:  # Show detailed results for first 3 runs
            print(f"\n📊 Run {run + 1} Results:")
            print(f"   Shared key length: {result['matching_bases']}")
            print(f"   Error rate: {result['error_rate']:.3f}")
            print(f"   Eavesdropper detected: {result['eavesdropper_detected']}")
    
    # Create comprehensive visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Error rates histogram
    axes[0, 0].hist(error_rates, bins=10, color='lightcoral', alpha=0.7)
    axes[0, 0].set_title('Error Rates Distribution')
    axes[0, 0].set_xlabel('Error Rate')
    axes[0, 0].set_ylabel('Frequency')
    
    # Key lengths histogram
    axes[0, 1].hist(key_lengths, bins=10, color='skyblue', alpha=0.7)
    axes[0, 1].set_title('Key Length Distribution')
    axes[0, 1].set_xlabel('Key Length')
    axes[0, 1].set_ylabel('Frequency')
    
    # Eavesdropper detection pie chart
    detected_count = sum(eavesdropper_detected)
    not_detected_count = len(eavesdropper_detected) - detected_count
    axes[1, 0].pie([detected_count, not_detected_count], 
                   labels=['Eavesdropper Detected', 'No Eavesdropper Detected'],
                   colors=['red', 'green'], autopct='%1.1f%%')
    axes[1, 0].set_title('Eavesdropper Detection')
    
    # Success rate bar chart
    success_rate = (len([r for r in results if r['error_rate'] < 0.1]) / len(results)) * 100
    axes[1, 1].bar(['Protocol Success Rate'], [success_rate], color='lightgreen')
    axes[1, 1].set_title('Protocol Success Rate')
    axes[1, 1].set_ylabel('Success Rate (%)')
    axes[1, 1].set_ylim(0, 100)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print(f"\n📈 Simulation Summary ({num_runs} runs):")
    print(f"Average error rate: {np.mean(error_rates):.3f} ± {np.std(error_rates):.3f}")
    print(f"Average key length: {np.mean(key_lengths):.1f} ± {np.std(key_lengths):.1f}")
    print(f"Eavesdropper detection rate: {detected_count/num_runs*100:.1f}%")
    print(f"Protocol success rate: {success_rate:.1f}%")
    
    return results

# ============================================================================
# SECTION 5: GITHUB COPILOT INTEGRATION EXAMPLES
# ============================================================================

def copilot_assisted_quantum_circuit(num_qubits: int) -> qt.Qobj:
    """
    Example of how GitHub Copilot can help create quantum circuits.
    
    This function demonstrates the kind of code that Copilot can help generate
    when you provide clear comments and function signatures.
    
    Args:
        num_qubits: Number of qubits in the circuit
        
    Returns:
        Quantum circuit as a unitary operator
    """
    print("💡 GitHub Copilot Integration Example")
    print("=" * 40)
    print("This function shows how Copilot can help with quantum coding:")
    print("1. Clear function signature with types")
    print("2. Descriptive docstring")
    print("3. Step-by-step implementation plan")
    print("4. Error handling considerations")
    
    # TODO: Implement quantum circuit creation with Copilot's help
    # Steps that Copilot can assist with:
    # 1. Create initial quantum state
    # 2. Apply quantum gates (Hadamard, CNOT, etc.)
    # 3. Handle measurement operations
    # 4. Implement error correction
    
    # Placeholder implementation
    circuit = qt.qeye(2**num_qubits)
    print(f"\n🔧 Generated quantum circuit for {num_qubits} qubits")
    print("💡 Tip: Use Copilot to expand this implementation!")
    
    return circuit

def quantum_error_correction_template(encoded_state: qt.Qobj, 
                                    error_type: str = 'bit_flip') -> Tuple[qt.Qobj, Dict]:
    """
    Template for quantum error correction implementation.
    
    This is designed to work with GitHub Copilot for automatic code generation.
    
    Args:
        encoded_state: The quantum state to correct
        error_type: Type of error ('bit_flip', 'phase_flip', 'both')
        
    Returns:
        Tuple of (corrected_state, error_syndrome_info)
    """
    print(f"🔧 Quantum Error Correction Template for {error_type} errors")
    print("=" * 50)
    print("This template is designed for Copilot to expand upon:")
    print("1. Create ancilla qubits for syndrome measurement")
    print("2. Apply appropriate error correction gates")
    print("3. Measure error syndromes")
    print("4. Apply correction based on syndrome")
    print("5. Return corrected state and syndrome info")
    
    # TODO: Implement quantum error correction with Copilot
    # Start typing here and let Copilot suggest the implementation!
    
    # Placeholder return
    return encoded_state, {"error_type": error_type, "correction_applied": False}

# ============================================================================
# SECTION 6: PRACTICAL EXERCISES
# ============================================================================

def quantum_teleportation_exercise():
    """
    Exercise: Implement quantum teleportation protocol.
    
    This function provides a template for implementing quantum teleportation
    with the help of GitHub Copilot.
    """
    print("🚀 Exercise: Quantum Teleportation Implementation")
    print("=" * 50)
    print("Use Copilot to help implement this function!")
    print("\nSteps to implement:")
    print("1. Create Bell pair (entangled qubits)")
    print("2. Apply Bell measurement")
    print("3. Apply conditional operations based on measurement")
    print("4. Return teleported qubit")
    
    def quantum_teleportation(qubit_to_teleport: qt.Qobj) -> Tuple[qt.Qobj, Dict]:
        """
        Implement quantum teleportation protocol.
        
        Args:
            qubit_to_teleport: The qubit to teleport
            
        Returns:
            Tuple of (teleported_qubit, classical_measurement_results)
        """
        # TODO: Implement quantum teleportation with Copilot
        # Start typing here and let AI assist you!
        
        pass
    
    print("\n💡 Tip: Place cursor after 'pass' and start implementing!")
    print("   Copilot will suggest quantum operations based on your comments.")
    
    return quantum_teleportation

# ============================================================================
# SECTION 7: MAIN EXECUTION AND DEMONSTRATION
# ============================================================================

def main():
    """Main function to run the quantum networking demonstration."""
    
    print("\n🎯 Quantum Networking with BB84 Protocol - Main Demonstration")
    print("=" * 70)
    
    # 1. Demonstrate quantum superposition
    demonstrate_quantum_superposition()
    
    # 2. Test BB84 protocol (no eavesdropper)
    print("\n" + "="*70)
    print("🧪 Testing BB84 Protocol (No Eavesdropper)")
    bb84_secure = BB84Protocol(key_length=50)
    result_secure = bb84_secure.run_protocol(eavesdropper_interference=False)
    
    # 3. Test BB84 protocol (with eavesdropper)
    print("\n" + "="*70)
    print("🧪 Testing BB84 Protocol (With Eavesdropper)")
    bb84_insecure = BB84Protocol(key_length=50)
    result_insecure = bb84_insecure.run_protocol(eavesdropper_interference=True)
    
    # 4. Run multiple simulations
    print("\n" + "="*70)
    print("🔄 Running Multiple BB84 Simulations")
    results = run_multiple_bb84_simulations(key_length=30, 
                                          eavesdropper_present=False, 
                                          num_runs=10)
    
    # 5. Demonstrate Copilot integration
    print("\n" + "="*70)
    print("🤖 GitHub Copilot Integration Examples")
    copilot_assisted_quantum_circuit(3)
    quantum_error_correction_template(qt.basis(2, 0), 'bit_flip')
    quantum_teleportation_exercise()
    
    # 6. Final summary
    print("\n" + "="*70)
    print("🏁 Quantum Networking Demonstration Complete!")
    print("\n📚 What You've Learned:")
    print("✅ Quantum networking fundamentals")
    print("✅ BB84 protocol implementation")
    print("✅ Interactive quantum simulations")
    print("✅ AI-assisted quantum coding")
    
    print("\n🚀 Next Steps:")
    print("1. Experiment with different protocol parameters")
    print("2. Implement additional quantum protocols")
    print("3. Use GitHub Copilot for quantum algorithm development")
    print("4. Explore advanced quantum networking topics")
    
    print("\n💡 Remember: Copilot is your quantum coding partner!")

if __name__ == "__main__":
    main()
