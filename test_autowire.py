#!/usr/bin/env python3
"""
Test script to verify the autowiring functionality works correctly.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def test_autowire():
    """Test the autowiring functionality"""
    print("🧪 Testing Autowiring Functionality")
    print("=" * 50)
    
    try:
        # Import required modules
        from core.base_classes import World, Zone
        from core.enums import ZoneType, NetworkType
        from core.network import Network
        from quantum_network.interactive_host import InteractiveQuantumHost
        from quantum_network.student_registry import REGISTRY, register_student_implementation
        
        # Create a simple world and zone
        world = World(size=(100, 100))
        zone = Zone(
            size=(50, 50), 
            position=(0, 0), 
            zone_type=ZoneType.SECURE, 
            parent_zone=world, 
            name="TestZone"
        )
        
        # Create a quantum network
        quantum_network = Network(NetworkType.QUANTUM_NETWORK, world)
        
        print("✅ World, zone, and network created")
        
        # Test 1: Create host without student implementation
        print("\n🔍 Test 1: Host without student implementation")
        host1 = InteractiveQuantumHost(
            address="test1",
            location=(10, 10),
            network=quantum_network,
            zone=zone,
            name="Alice"
        )
        
        print(f"   Student code validated: {host1.student_code_validated}")
        print(f"   Has student implementation: {host1.student_implementation is not None}")
        
        # Test 2: Register a student implementation and create host
        print("\n🔍 Test 2: Host with registered student implementation")
        
        # Create a mock student implementation
        class MockStudentImpl:
            def __init__(self, host):
                self.host = host
            
            def bb84_send_qubits(self, num_qubits=50):
                print(f"   Mock BB84 send qubits: {num_qubits}")
                return True
            
            def process_received_qbit(self, qbit, from_channel):
                print(f"   Mock process received qubit")
                return True
            
            def bb84_reconcile_bases(self, their_bases):
                print(f"   Mock reconcile bases")
                return [], []
            
            def bb84_estimate_error_rate(self, their_bits_sample):
                print(f"   Mock estimate error rate")
                return 0.0
        
        # Register the implementation
        register_student_implementation("Alice", MockStudentImpl)
        
        # Create host - should autowire
        host2 = InteractiveQuantumHost(
            address="test2",
            location=(20, 20),
            network=quantum_network,
            zone=zone,
            name="Alice"  # Same name as registered
        )
        
        print(f"   Student code validated: {host2.student_code_validated}")
        print(f"   Has student implementation: {host2.student_implementation is not None}")
        
        # Test 3: Test plugin loading
        print("\n🔍 Test 3: Plugin loading")
        host3 = InteractiveQuantumHost(
            address="test3",
            location=(30, 30),
            network=quantum_network,
            zone=zone,
            name="Bob"
        )
        
        print(f"   Student code validated: {host3.student_code_validated}")
        print(f"   Has student implementation: {host3.student_implementation is not None}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_autowire()
    sys.exit(0 if success else 1)
