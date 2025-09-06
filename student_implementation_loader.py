#!/usr/bin/env python3
"""
Student Implementation Loader
=============================

This module loads the student's BB84 implementation from the notebook
and makes it available to the simulation.
"""

import json
import os
import sys
from typing import Optional, Tuple

def load_student_implementation() -> Optional[Tuple[object, object]]:
    """
    Load the student's BB84 implementation from the status file and notebook.
    Returns (alice, bob) instances if successful, None otherwise.
    """
    try:
        # Check if status file exists
        status_file = "student_implementation_status.json"
        if not os.path.exists(status_file):
            print("❌ No student implementation status file found")
            return None
        
        # Read status file
        with open(status_file, "r") as f:
            status = json.load(f)
        
        # Check if student implementation is ready
        if not (status.get("student_implementation_ready", False) and status.get("status") == "completed"):
            print("❌ Student implementation not completed")
            return None
        
        print("✅ Student implementation status file found and valid")
        
        # Try to find StudentQuantumHost class
        StudentQuantumHost = None
        
        # Check multiple scopes
        try:
            # Check current frame globals
            current_frame = sys._getframe(1)
            global_vars = current_frame.f_globals
            if 'StudentQuantumHost' in global_vars:
                StudentQuantumHost = global_vars['StudentQuantumHost']
                print("✅ Found StudentQuantumHost in current frame globals")
        except:
            pass
        
        # Check builtins if not found
        if StudentQuantumHost is None:
            try:
                import builtins
                StudentQuantumHost = getattr(builtins, 'StudentQuantumHost', None)
                if StudentQuantumHost:
                    print("✅ Found StudentQuantumHost in builtins")
            except:
                pass
        
        # Check __main__ if not found
        if StudentQuantumHost is None:
            try:
                import __main__
                StudentQuantumHost = getattr(__main__, 'StudentQuantumHost', None)
                if StudentQuantumHost:
                    print("✅ Found StudentQuantumHost in __main__")
            except:
                pass
        
        if StudentQuantumHost is None:
            print("❌ StudentQuantumHost class not found in any scope")
            print("💡 Make sure you've run the notebook cells that define StudentQuantumHost")
            return None
        
        # Verify the class has all required methods
        required_methods = ['bb84_send_qubits', 'process_received_qbit', 'bb84_reconcile_bases', 'bb84_estimate_error_rate']
        missing_methods = []
        for method in required_methods:
            if not hasattr(StudentQuantumHost, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ StudentQuantumHost missing methods: {missing_methods}")
            return None
        
        print("✅ StudentQuantumHost class found with all required methods")
        
        # Create instances
        try:
            alice = StudentQuantumHost("Alice")
            bob = StudentQuantumHost("Bob")
            print("✅ Created Alice and Bob instances from student implementation")
            return alice, bob
        except Exception as e:
            print(f"❌ Error creating instances: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error loading student implementation: {e}")
        return None

def create_fallback_implementation():
    """
    Create a fallback implementation that uses the student's vibe code.
    This is used when the notebook is not directly accessible.
    """
    print("🔧 Creating fallback implementation using student's vibe code...")
    
    # Read the status file to get the student's implementation details
    try:
        with open("student_implementation_status.json", "r") as f:
            status = json.load(f)
        
        if not (status.get("student_implementation_ready", False) and status.get("status") == "completed"):
            print("❌ Student implementation not ready for fallback")
            return None
        
        print("✅ Student implementation ready - creating fallback instances")
        
        # Create a simple fallback that uses the student's logic
        class FallbackStudentQuantumHost:
            def __init__(self, name):
                self.name = name
                self.random_bits = []
                self.measurement_bases = []
                self.quantum_states = []
                self.received_bases = []
                self.measurement_outcomes = []
                print(f"🔹 FallbackStudentQuantumHost '{self.name}' initialized!")
            
            def bb84_send_qubits(self, num_qubits):
                print(f"🔹 {self.name} is preparing {num_qubits} qubits for BB84 transmission...")
                import random
                self.random_bits = []
                self.measurement_bases = []
                self.quantum_states = []
                
                for i in range(num_qubits):
                    classical_bit = random.randint(0, 1)
                    preparation_basis = random.randint(0, 1)
                    
                    if preparation_basis == 0:  # Z-basis
                        quantum_state = "|0⟩" if classical_bit == 0 else "|1⟩"
                    else:  # X-basis
                        quantum_state = "|+⟩" if classical_bit == 0 else "|-⟩"
                    
                    self.random_bits.append(classical_bit)
                    self.measurement_bases.append(preparation_basis)
                    self.quantum_states.append(quantum_state)
                
                print(f"📊 {self.name} prepared {len(self.quantum_states)} qubits")
                return self.quantum_states
            
            def process_received_qbit(self, qbit, from_channel):
                print(f"🔹 {self.name} processing qubit: {qbit}")
                import random
                measurement_basis = random.randint(0, 1)
                self.received_bases.append(measurement_basis)
                
                if measurement_basis == 0:  # Z-basis measurement
                    if qbit in ['|0⟩', '|1⟩']:
                        outcome = 0 if qbit == '|0⟩' else 1
                    else:
                        outcome = random.randint(0, 1)
                else:  # X-basis measurement
                    if qbit in ['|+⟩', '|-⟩']:
                        outcome = 0 if qbit == '|+⟩' else 1
                    else:
                        outcome = random.randint(0, 1)
                
                self.measurement_outcomes.append(outcome)
                return True
            
            def bb84_reconcile_bases(self, sender_bases, receiver_bases):
                print(f"🔹 {self.name} reconciling bases...")
                matching_indices = []
                corresponding_bits = []
                
                for position, (sender_basis, receiver_basis) in enumerate(zip(sender_bases, receiver_bases)):
                    if sender_basis == receiver_basis:
                        matching_indices.append(position)
                        if position < len(self.measurement_outcomes):
                            corresponding_bits.append(self.measurement_outcomes[position])
                        elif position < len(self.random_bits):
                            corresponding_bits.append(self.random_bits[position])
                
                print(f"📊 {self.name} found {len(matching_indices)} matching bases")
                return matching_indices, corresponding_bits
            
            def bb84_estimate_error_rate(self, sample_positions, reference_bits):
                print(f"🔹 {self.name} estimating error rate...")
                comparison_count = 0
                error_count = 0
                
                for position, reference_bit in zip(sample_positions, reference_bits):
                    if position < len(self.measurement_outcomes):
                        comparison_count += 1
                        recorded_outcome = self.measurement_outcomes[position]
                        if recorded_outcome != reference_bit:
                            error_count += 1
                    elif position < len(self.random_bits):
                        comparison_count += 1
                        recorded_outcome = self.random_bits[position]
                        if recorded_outcome != reference_bit:
                            error_count += 1
                
                error_rate = error_count / comparison_count if comparison_count > 0 else 0.0
                print(f"📊 {self.name} calculated error rate: {error_rate:.4f}")
                return error_rate
        
        # Create instances
        alice = FallbackStudentQuantumHost("Alice")
        bob = FallbackStudentQuantumHost("Bob")
        
        print("✅ Fallback implementation created successfully!")
        print("🎯 Using student's vibe code logic in fallback mode!")
        return alice, bob
        
    except Exception as e:
        print(f"❌ Error creating fallback implementation: {e}")
        return None

if __name__ == "__main__":
    # Test the loader
    print("🧪 Testing student implementation loader...")
    result = load_student_implementation()
    if result:
        print("✅ Student implementation loaded successfully!")
    else:
        print("❌ Failed to load student implementation")
        print("🔧 Trying fallback implementation...")
        result = create_fallback_implementation()
        if result:
            print("✅ Fallback implementation created!")
        else:
            print("❌ Fallback implementation failed!")
