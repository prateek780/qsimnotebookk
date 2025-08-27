# Introduction to Quantum Networking

Quantum networking leverages the principles of quantum mechanics to enable secure communication and distributed quantum computing. Unlike classical networks, quantum networks use qubits and quantum entanglement to transmit information, offering fundamentally new capabilities such as unbreakable encryption and quantum teleportation.

In this project, you'll explore quantum key distribution (QKD) using the BB84 protocol, a foundational algorithm in quantum networking. This notebook is part of a broader simulation project that models both classical and quantum networks, helping you understand how quantum technologies integrate with real-world systems.
# BB84 Protocol: Step-by-Step Overview

Before we dive into coding, let's understand how BB84 works in practice:

## 1. Qubit Preparation (Alice's Side)
- Alice generates random bits (0s and 1s)
- For each bit, she randomly chooses a basis:
  - Rectilinear (↕ ↔) = Computational Basis
  - Diagonal (↗↙ ↖↘) = Hadamard Basis
- She encodes each bit in its chosen basis

## 2. Quantum Transmission
- Alice sends qubits to Bob through quantum channel
- Each qubit maintains its quantum state unless disturbed
- Any eavesdropping attempt disturbs the quantum states

## 3. Measurement (Bob's Side)
- For each received qubit, Bob randomly chooses a measurement basis
- He doesn't know which basis Alice used
- Records his measurement results

## 4. Key Sifting
- Alice and Bob publicly share their basis choices
- They keep only the bits where they used the same basis
- These bits become their potential shared key

## 5. Error Detection
- They compare a subset of their shared bits
- If error rate is low: proceed with the key
- If error rate is high: potential eavesdropping detected

## 6. Final Key
- The remaining uncompared bits become the shared secret key
- This key is guaranteed to be secure by quantum mechanics

In this notebook, we'll implement each of these steps, allowing you to see quantum key distribution in action!
# Let's implement BB84 protocol step by step!
Welcome! In this notebook, you'll implement the BB84 quantum key distribution protocol from scratch. We'll focus purely on coding, with clear steps and minimal distractions. Let's get started!
# Setup: Import required libraries
import numpy as np
import random
## Here's the BB84 class structure. You implement the methods!
Below is the BB84Protocol class. Your task is to fill in the TODOs for each method. Each method represents a key step in the BB84 protocol. Follow the comments and hints to implement the logic step by 
.
# Understanding Quantum Bases in BB84

Before diving into the code, let's understand the two key quantum bases used in BB84:

## 1. Computational Basis (0)
- This is the standard basis {|0⟩, |1⟩}
- Think of it as measuring "up/down" or "0/1" directly
- When measuring in this basis:
  - |0⟩ gives 0 with 100% probability
  - |1⟩ gives 1 with 100% probability

## 2. Hadamard Basis (1)
- This basis uses superposition states {|+⟩, |-⟩}
- |+⟩ = (|0⟩ + |1⟩)/√2  (represents 0 in Hadamard basis)
- |-⟩ = (|0⟩ - |1⟩)/√2  (represents 1 in Hadamard basis)
- It's like measuring "diagonal" instead of "up/down"
- Key property: If you measure a state prepared in computational basis using Hadamard basis (or vice versa), you get random results!

## Why Two Bases?
This is the key to BB84's security! If Eve doesn't know which basis was used, she can't measure without potentially disturbing the state and revealing her presence. This is quantum mechanics in action!
class BB84Protocol:
    def __init__(self, num_qubits=20, eavesdropper=False):
        self.num_qubits = num_qubits
        self.eavesdropper = eavesdropper
        self.alice_bits = []
        self.alice_bases = []
        self.encoded_qubits = []
        self.bob_bases = []
        self.bob_results = []
        self.shared_key = []
        self.error_rate = 0.0

    def alice_prepare_qubits(self):
        """
        Generate random bits and bases for Alice and store them.
        TODO:
        1. Generate self.alice_bits:
           - Use random.randint(0, 1) or random.choice([0, 1])
           - Create a list of num_qubits random bits
           
        2. Generate self.alice_bases:
           - Similar to bits, generate random 0s (computational) and 1s (Hadamard)
           - Each basis choice should be independent
           
        Technical Note:
        - The random bits will become the key if bases match
        - The bases determine how qubits are encoded (|0⟩,|1⟩ vs |+⟩,|-⟩)
        """
        pass

    def encode_qubit(self, bit, basis):
        """
        Encode a classical bit as a qubit in the given basis.
        
        TODO:
        1. For computational basis (0):
           - If bit=0: return '|0⟩' (represents spin-up state)
           - If bit=1: return '|1⟩' (represents spin-down state)
           
        2. For Hadamard basis (1):
           - If bit=0: return '|+⟩' (superposition: (|0⟩ + |1⟩)/√2)
           - If bit=1: return '|-⟩' (superposition: (|0⟩ - |1⟩)/√2)
           
        Technical Note:
        - In real quantum systems, these states would be actual quantum superpositions
        - Here we simulate them with string representations
        - The Hadamard basis states are equal superpositions with different phases
        """
        pass

    def bob_measure_qubits(self):
        """
        Simulate Bob's quantum measurements of the received qubits.
        
        TODO:
        1. Generate Bob's random basis choices:
           - Like Alice, create list of random 0s and 1s
           - Store in self.bob_bases
           
        2. Simulate measurements:
           For each qubit:
           a) If Eve is present:
              - Generate random basis for Eve
              - If Eve's basis matches encoding: she gets correct result
              - If mismatch: she gets random result
              - Eve's measurement disturbs the state!
           
           b) Bob's measurement:
              - If bases match (Bob's = original encoding):
                * Get deterministic result matching original bit
              - If bases mismatch:
                * Get random result (0 or 1 with 50% probability)
        
        Technical Note:
        - This simulates quantum measurement collapse
        - Measuring in wrong basis randomizes the outcome
        - Eavesdropping creates detectable errors
        """
        pass

    def establish_shared_key(self):
        """
        Compare bases and establish the final shared key.
        
        TODO:
        1. Find matching bases:
           - Compare self.alice_bases with self.bob_bases
           - Keep track of indices where they match
           
        2. Build shared key:
           - For matching bases only:
              * Add corresponding bits to self.shared_key
              * Compare Alice's bits with Bob's results
              * Count mismatches to calculate error rate
           
        3. Calculate error rate:
           - error_rate = (mismatched_bits) / (total_matching_bases)
           
        Technical Note:
        - Error rate > 0 could indicate eavesdropping
        - Theoretical error with Eve: ~25% (from quantum mechanics)
        - No Eve: error rate should be ~0%
        """
        pass

    def run_protocol(self):
        """
        Orchestrate the BB84 protocol steps:
        1. Alice prepares qubits
        2. Alice encodes qubits
        3. Bob measures qubits (with/without eavesdropper)
        4. Establish shared key and calculate error rate
        
        Technical Note:
        - This simulates the complete quantum key distribution
        - In real QKD, additional steps like error correction and
          privacy amplification would follow
        """
        self.alice_prepare_qubits()
        self.encoded_qubits = [self.encode_qubit(bit, basis) for bit, basis in zip(self.alice_bits, self.alice_bases)]
        self.bob_measure_qubits()
        self.establish_shared_key()
protocol = BB84Protocol()
protocol.alice_prepare_qubits()
# Helper functions and simple testing framework

def print_protocol_results(protocol):
    print("Shared key:", protocol.shared_key)
    print("Key length:", len(protocol.shared_key))
    print("Error rate: {:.2f}%".format(protocol.error_rate * 100))

def run_bb84_test(num_qubits=20, eavesdropper=False):
    print("Running BB84 Protocol with {} qubits. Eavesdropper: {}".format(num_qubits, eavesdropper))
    protocol = BB84Protocol(num_qubits=num_qubits, eavesdropper=eavesdropper)
    protocol.run_protocol()
    print_protocol_results(protocol)
    if eavesdropper:
        if protocol.error_rate > 0.2:
            print("Eavesdropper detected! High error rate.")
        else:
            print("No significant eavesdropping detected.")
    print("-" * 40)
# Test BB84 without eavesdropper
run_bb84_test(num_qubits=20, eavesdropper=False)
# Test BB84 with eavesdropper
run_bb84_test(num_qubits=20, eavesdropper=True)
## Vibe Coding Tips: Using GitHub Copilot for BB84

- **Generate random bits for Alice:**  
  _"Generate a list of random 0s and 1s for Alice's bits"_

- **Create measurement bases for Bob:**  
  _"For each qubit, randomly choose 0 (computational) or 1 (Hadamard) as Bob's basis"_

- **Compare Alice's and Bob's bases:**  
  _"Find indices where Alice's and Bob's bases match and keep those bits"_

- **Calculate error rate between measurements:**  
  _"Compute the fraction of mismatched bits in the shared key"_

- **Simulate eavesdropping:**  
  _"If eavesdropper is enabled, simulate Eve's random basis measurement before Bob"_

Use these prompts with Copilot to help you implement each method. Focus on the logic, keep it simple, and enjoy coding the BB84 protocol!
# BB84 Vibe Coding: Hands-On Quantum Key Distribution
Welcome to the coding section! Here, you'll implement the BB84 protocol step by step, simulating quantum key distribution as part of a larger quantum-classical network simulation.

- **Why BB84?**  The BB84 protocol is a cornerstone of quantum networking, enabling secure key exchange using quantum bits (qubits).
- **Your Mission:**  Code each part of the protocol, experiment with eavesdropping, and see how quantum security works in practice.
- **Project Connection:**  This notebook is integrated with the main simulation project, which models both classical and quantum networks. Your BB84 implementation can be extended or connected to other modules (see `classical_network/`, `quantum_network/`, and `core/` folders) to simulate real-world scenarios.
- **Copilot for Help:**  Use GitHub Copilot as your coding partner! Copilot can suggest code, explain concepts, and help you debug as you work through each step. Try using the tips below or ask Copilot for help if you get stuck.

Let's dive in and bring quantum networking to life with code!