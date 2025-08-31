#!/usr/bin/env python3
"""
Integration Test for Student BB84 Implementation
===============================================

This script tests the complete integration between the Jupyter notebook
student implementation and the quantum network simulation.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def create_mock_student_implementation():
    """Create a mock student implementation for testing"""
    
    # Create mock student implementation class
    mock_implementation = '''
import random
try:
    import qutip as qt
except Exception:
    qt = None

class MockStudentImplementation:
    """Mock student BB84 implementation for testing"""
    
    def __init__(self, host=None):
        self.host = host
        self.basis_choices = []
        self.measurement_outcomes = []
        self.shared_bases_indices = []
        print("🧪 Mock student implementation created for testing")
    
    def bb84_send_qubits(self, num_qubits=50):
        """Mock BB84 qubit sending"""
        print(f"🧪 Mock: Sending {num_qubits} qubits")
        
        # Reset state
        self.basis_choices = []
        self.measurement_outcomes = []
        
        # Generate random bits and bases
        for _ in range(num_qubits):
            basis = random.choice(['Z', 'X'])
            bit = random.choice([0, 1])
            self.basis_choices.append(basis)
            self.measurement_outcomes.append(bit)
        
        # Simulate sending qubits
        if self.host:
            channel = self.host.get_channel()
            if channel:
                for i in range(num_qubits):
                    # Create mock qubit
                    if qt:
                        if self.basis_choices[i] == 'Z':
                            qubit = qt.basis(2, self.measurement_outcomes[i])
                        else:
                            if self.measurement_outcomes[i] == 0:
                                qubit = (qt.basis(2, 0) + qt.basis(2, 1)).unit()
                            else:
                                qubit = (qt.basis(2, 0) - qt.basis(2, 1)).unit()
                    else:
                        qubit = (self.basis_choices[i], self.measurement_outcomes[i])
                    
                    # Send qubit
                    self.host.send_qubit(qubit, channel)
        
        print(f"🧪 Mock: Sent {num_qubits} qubits with bases {self.basis_choices[:10]}...")
        return True
    
    def process_received_qbit(self, qbit, from_channel):
        """Mock qubit processing"""
        # Random basis choice
        basis = random.choice(['Z', 'X'])
        
        # Mock measurement
        if qt and hasattr(qt, 'Qobj') and isinstance(qbit, qt.Qobj):
            if basis == 'Z':
                proj0 = qt.ket2dm(qt.basis(2, 0))
            else:
                proj0 = qt.ket2dm((qt.basis(2, 0) + qt.basis(2, 1)).unit())
            p0 = qt.expect(proj0, qbit)
            outcome = 0 if random.random() < p0 else 1
        else:
            outcome = random.choice([0, 1])
        
        self.basis_choices.append(basis)
        self.measurement_outcomes.append(outcome)
        
        print(f"🧪 Mock: Received qubit, measured {outcome} in {basis} basis")
        return True
    
    def bb84_reconcile_bases(self, their_bases):
        """Mock basis reconciliation"""
        self.shared_bases_indices = [
            i for i, (b1, b2) in enumerate(zip(self.basis_choices, their_bases))
            if b1 == b2
        ]
        
        print(f"🧪 Mock: Found {len(self.shared_bases_indices)} shared bases")
        
        # Send shared indices
        if self.host:
            self.host.send_classical_data({
                'type': 'shared_bases_indices',
                'data': self.shared_bases_indices
            })
        
        return True
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """Mock error rate estimation"""
        num_errors = 0
        for their_bit, i in their_bits_sample:
            if i < len(self.measurement_outcomes):
                if self.measurement_outcomes[i] != their_bit:
                    num_errors += 1
        
        error_rate = num_errors / len(their_bits_sample) if their_bits_sample else 0
        print(f"🧪 Mock: Estimated error rate: {error_rate:.3f}")
        
        # Complete QKD
        if self.host:
            self.host.send_classical_data({'type': 'complete'})
        
        return error_rate

# Alias for bridge compatibility
StudentImplementationBridge = MockStudentImplementation
'''
    
    # Write mock implementation file
    with open("mock_student_impl.py", "w", encoding="utf-8") as f:
        f.write(mock_implementation)
    
    # Create status file
    status = {
        "student_implementation_ready": True,
        "student_plugin_module": "mock_student_impl",
        "student_plugin_class": "StudentImplementationBridge",
        "implementation_type": "MockImplementation",
        "methods_implemented": [
            "bb84_send_qubits",
            "process_received_qbit", 
            "bb84_reconcile_bases",
            "bb84_estimate_error_rate"
        ]
    }
    
    with open("student_implementation_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
    
    print("✅ Mock student implementation created")

def test_notebook_bridge():
    """Test the notebook bridge functionality"""
    print("\n🧪 Testing notebook bridge...")
    
    try:
        from quantum_network.notebook_bridge import check_simulation_readiness, NotebookIntegration
        
        # Check readiness
        readiness = check_simulation_readiness()
        print(f"   Readiness check: {readiness}")
        
        if not readiness.get("ready", False):
            print("❌ Simulation not ready")
            return False
        
        # Test integration
        integration = NotebookIntegration()
        bridge = integration.load_student_implementation()
        
        if bridge:
            print("✅ Notebook bridge working")
            return True
        else:
            print("❌ Failed to load student implementation")
            return False
            
    except Exception as e:
        print(f"❌ Notebook bridge test failed: {e}")
        return False

def test_interactive_host():
    """Test InteractiveQuantumHost with student implementation"""
    print("\n🧪 Testing InteractiveQuantumHost...")
    
    try:
        from quantum_network.interactive_host import InteractiveQuantumHost
        from quantum_network.notebook_bridge import NotebookIntegration
        from core.network import Network
        from core.enums import NetworkType
        
        # Load student implementation
        integration = NotebookIntegration()
        bridge = integration.load_student_implementation()
        
        if not bridge:
            print("❌ No student implementation available")
            return False
        
        # Create test network
        network = Network(network_type=NetworkType.QUANTUM_NETWORK, location=(0, 0), name="Test Network")
        
        # Create host with student implementation
        host = InteractiveQuantumHost(
            address="test_host",
            location=(0, 0),
            network=network,
            name="Test Host",
            student_implementation=bridge
        )
        
        # Check validation
        if host.student_code_validated:
            print("✅ InteractiveQuantumHost working with student implementation")
            return True
        else:
            print("❌ Student implementation not validated")
            return False
            
    except Exception as e:
        print(f"❌ InteractiveQuantumHost test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quantum_encryption():
    """Test quantum encryption utilities"""
    print("\n🧪 Testing quantum encryption...")
    
    try:
        from utils.quantum_encryption import quantum_xor_encrypt, quantum_xor_decrypt, QuantumSecureMessenger
        import random
        
        # Generate test key
        test_key = [random.randint(0, 1) for _ in range(256)]
        
        # Test basic encryption
        message = "Hello, Quantum World!"
        encrypted, metadata = quantum_xor_encrypt(message, test_key)
        decrypted = quantum_xor_decrypt(encrypted, test_key, metadata)
        
        if message == decrypted:
            print("✅ Basic quantum encryption working")
        else:
            print("❌ Basic quantum encryption failed")
            return False
        
        # Test secure messenger
        messenger = QuantumSecureMessenger(test_key, test_key.copy())
        message_data = messenger.send_message("Alice", "Test message", "quantum_xor")
        received = messenger.receive_message(message_data, "Bob")
        
        if received == "Test message":
            print("✅ Quantum secure messenger working")
            return True
        else:
            print("❌ Quantum secure messenger failed")
            return False
            
    except Exception as e:
        print(f"❌ Quantum encryption test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_simulation():
    """Test the complete simulation"""
    print("\n🧪 Testing complete simulation...")
    
    try:
        import complete_simulation
        
        # Create simulation instance
        simulation = complete_simulation.QuantumNetworkSimulation()
        
        # Check student implementation
        if not simulation.check_student_implementation():
            print("❌ Student implementation check failed")
            return False
        
        print("✅ Complete simulation can initialize")
        print("⚠️ Full simulation test requires more time - skipping for quick test")
        return True
        
    except Exception as e:
        print(f"❌ Complete simulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "mock_student_impl.py",
        "student_implementation_status.json",
        "simulation_report.json",
        "quantum_conversation.json"
    ]
    
    for filename in test_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 QUANTUM NETWORK INTEGRATION TESTS")
    print("="*50)
    
    # Setup
    print("🔧 Setting up test environment...")
    create_mock_student_implementation()
    
    tests = [
        ("Notebook Bridge", test_notebook_bridge),
        ("Interactive Host", test_interactive_host), 
        ("Quantum Encryption", test_quantum_encryption),
        ("Complete Simulation", test_complete_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*20}")
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("🎯 INTEGRATION TEST RESULTS")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Integration is working!")
        success_rate = 100.0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        success_rate = (passed / total) * 100
    
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
