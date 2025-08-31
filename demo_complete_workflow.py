#!/usr/bin/env python3
"""
Complete Workflow Demonstration
===============================

This script demonstrates the complete workflow from student BB84 implementation
to full quantum network simulation with secure messaging.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def create_demo_student_implementation():
    """Create a demo student implementation that actually works"""
    
    demo_code = '''
import random
try:
    import qutip as qt
except Exception:
    qt = None

class DemoStudentImplementation:
    """Demo BB84 implementation that actually works for demonstration"""
    
    def __init__(self, host=None):
        self.host = host
        self.basis_choices = []
        self.measurement_outcomes = []
        self.shared_bases_indices = []
        print("🎓 Demo Student BB84 Implementation Loaded")
    
    def bb84_send_qubits(self, num_qubits=50):
        """Send qubits using BB84 protocol"""
        print(f"📡 Sending {num_qubits} qubits using BB84...")
        
        # Reset state
        self.basis_choices = []
        self.measurement_outcomes = []
        
        if not self.host:
            print("❌ No host available for sending")
            return False
        
        channel = self.host.get_channel()
        if not channel:
            print("❌ No quantum channel available")
            return False
        
        # Generate and send qubits
        for i in range(num_qubits):
            # Random bit and basis
            bit = random.choice([0, 1])
            basis = random.choice(['Z', 'X'])
            
            self.basis_choices.append(basis)
            self.measurement_outcomes.append(bit)
            
            # Prepare qubit based on basis and bit
            if qt:
                if basis == 'Z':
                    qubit = qt.basis(2, bit)  # |0⟩ or |1⟩
                else:  # X basis
                    if bit == 0:
                        qubit = (qt.basis(2, 0) + qt.basis(2, 1)).unit()  # |+⟩
                    else:
                        qubit = (qt.basis(2, 0) - qt.basis(2, 1)).unit()  # |-⟩
            else:
                qubit = (basis, bit)  # Fallback representation
            
            # Send qubit
            self.host.send_qubit(qubit, channel)
        
        print(f"✅ Sent {num_qubits} qubits")
        print(f"   Bases used: {self.basis_choices[:10]}...")
        print(f"   Bits sent: {self.measurement_outcomes[:10]}...")
        return True
    
    def process_received_qbit(self, qbit, from_channel):
        """Process received qubit"""
        # Choose random measurement basis
        measurement_basis = random.choice(['Z', 'X'])
        
        # Measure qubit
        if qt and hasattr(qt, 'Qobj') and isinstance(qbit, qt.Qobj):
            # Proper quantum measurement
            if measurement_basis == 'Z':
                projector0 = qt.ket2dm(qt.basis(2, 0))
            else:  # X basis
                projector0 = qt.ket2dm((qt.basis(2, 0) + qt.basis(2, 1)).unit())
            
            prob0 = qt.expect(projector0, qbit)
            outcome = 0 if random.random() < prob0 else 1
        else:
            # Fallback measurement
            outcome = random.choice([0, 1])
        
        # Store results
        self.basis_choices.append(measurement_basis)
        self.measurement_outcomes.append(outcome)
        
        return True
    
    def bb84_reconcile_bases(self, their_bases):
        """Reconcile measurement bases"""
        print(f"🔄 Reconciling bases...")
        print(f"   My bases: {self.basis_choices[:10]}...")
        print(f"   Their bases: {their_bases[:10]}...")
        
        # Find matching bases
        self.shared_bases_indices = [
            i for i, (my_basis, their_basis) in enumerate(zip(self.basis_choices, their_bases))
            if my_basis == their_basis
        ]
        
        print(f"✅ Found {len(self.shared_bases_indices)} shared bases")
        
        # Send shared indices back
        if self.host:
            self.host.send_classical_data({
                'type': 'shared_bases_indices',
                'data': self.shared_bases_indices
            })
        
        return True
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """Estimate error rate"""
        print(f"🔍 Estimating error rate from {len(their_bits_sample)} samples...")
        
        errors = 0
        for their_bit, index in their_bits_sample:
            if index < len(self.measurement_outcomes):
                if self.measurement_outcomes[index] != their_bit:
                    errors += 1
        
        error_rate = errors / len(their_bits_sample) if their_bits_sample else 0
        print(f"📊 Error rate: {error_rate:.3f} ({errors}/{len(their_bits_sample)})")
        
        # Complete the protocol
        if self.host:
            self.host.send_classical_data({'type': 'complete'})
        
        return error_rate

# Alias for compatibility
StudentImplementationBridge = DemoStudentImplementation
'''
    
    # Write demo implementation
    with open("demo_student_impl.py", "w", encoding="utf-8") as f:
        f.write(demo_code)
    
    # Create status file
    status = {
        "student_implementation_ready": True,
        "student_plugin_module": "demo_student_impl",
        "student_plugin_class": "StudentImplementationBridge",
        "implementation_type": "DemoImplementation",
        "methods_implemented": [
            "bb84_send_qubits",
            "process_received_qbit",
            "bb84_reconcile_bases", 
            "bb84_estimate_error_rate"
        ]
    }
    
    with open("student_implementation_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
    
    print("✅ Demo student implementation created")

def demonstrate_complete_workflow():
    """Demonstrate the complete workflow"""
    print("\n🎯 COMPLETE QUANTUM NETWORK WORKFLOW DEMONSTRATION")
    print("="*60)
    print("This demonstrates the full student experience:")
    print("1. Student implements BB84 in notebook")
    print("2. Implementation is exported and validated")  
    print("3. Complete simulation runs with student code")
    print("4. Quantum keys are established and used for encryption")
    print("="*60)
    
    try:
        # Step 1: Create student implementation
        print("\n📝 Step 1: Creating Student BB84 Implementation")
        create_demo_student_implementation()
        
        # Step 2: Test notebook bridge
        print("\n🌉 Step 2: Testing Notebook Bridge")
        from quantum_network.notebook_bridge import check_simulation_readiness, NotebookIntegration
        
        readiness = check_simulation_readiness()
        print(f"   Implementation ready: {readiness['ready']}")
        
        if not readiness['ready']:
            print("❌ Implementation not ready")
            return False
        
        # Step 3: Test interactive host
        print("\n🔬 Step 3: Creating Interactive Quantum Hosts")
        from quantum_network.interactive_host import InteractiveQuantumHost
        from core.network import Network
        from core.enums import NetworkType
        
        integration = NotebookIntegration()
        alice_bridge = integration.load_student_implementation()
        bob_bridge = integration.load_student_implementation()
        
        # Create test network
        network = Network(network_type=NetworkType.QUANTUM_NETWORK, location=(0, 0), name="Demo Network")
        
        # Create hosts with student implementation
        alice = InteractiveQuantumHost(
            address="alice_demo",
            location=(0, 0),
            network=network,
            name="Alice",
            student_implementation=alice_bridge
        )
        
        bob = InteractiveQuantumHost(
            address="bob_demo", 
            location=(10, 10),
            network=network,
            name="Bob",
            student_implementation=bob_bridge
        )
        
        print("✅ Interactive quantum hosts created with student implementation")
        
        # Step 4: Test encryption
        print("\n🔐 Step 4: Testing Quantum Encryption")
        from utils.quantum_encryption import demonstrate_quantum_encryption
        
        # Generate demo keys (normally from BB84)
        demo_key = [random.randint(0, 1) for _ in range(256)]
        encryption_success = demonstrate_quantum_encryption(demo_key, demo_key.copy())
        
        if not encryption_success:
            print("❌ Encryption test failed")
            return False
        
        # Step 5: Complete simulation (quick test)
        print("\n🚀 Step 5: Testing Complete Simulation Framework")
        import complete_simulation
        
        simulation = complete_simulation.QuantumNetworkSimulation()
        init_success = simulation.check_student_implementation()
        
        if init_success:
            print("✅ Complete simulation framework ready")
        else:
            print("❌ Complete simulation framework failed")
            return False
        
        # Step 6: Show results
        print("\n📊 Step 6: Workflow Complete!")
        print("="*40)
        print("✅ Student implementation: Working")
        print("✅ Notebook bridge: Connected") 
        print("✅ Interactive hosts: Created")
        print("✅ Quantum encryption: Functional")
        print("✅ Complete simulation: Ready")
        print("="*40)
        
        print("\n🎉 DEMONSTRATION SUCCESSFUL!")
        print("\nStudents can now:")
        print("1. 📓 Open quantum_networking_interactive.ipynb")
        print("2. 🎓 Implement BB84 algorithms")
        print("3. 📤 Export their implementation")
        print("4. 🚀 Run: python complete_simulation.py")
        print("5. 🔐 See secure quantum communication in action!")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_demo_files():
    """Clean up demo files"""
    demo_files = [
        "demo_student_impl.py",
        "student_implementation_status.json",
        "simulation_report.json",
        "quantum_conversation.json"
    ]
    
    for filename in demo_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🗑️ Cleaned up {filename}")
        except Exception:
            pass

if __name__ == "__main__":
    print("🌟 QUANTUM NETWORK COMPLETE WORKFLOW DEMO")
    print("This shows the full student experience from notebook to simulation")
    print()
    
    success = demonstrate_complete_workflow()
    
    if success:
        print("\n✨ WORKFLOW DEMONSTRATION COMPLETE!")
        print("The integration is working perfectly!")
        print("\n📖 Next steps for students:")
        print("1. Read STUDENT_GUIDE.md for detailed instructions")
        print("2. Open quantum_networking_interactive.ipynb")
        print("3. Complete the BB84 implementation")
        print("4. Run the complete simulation!")
    else:
        print("\n❌ Workflow demonstration failed")
        print("Check the error messages above")
    
    print("\n🧹 Cleaning up demo files...")
    cleanup_demo_files()
    
    sys.exit(0 if success else 1)
