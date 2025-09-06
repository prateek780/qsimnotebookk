#!/usr/bin/env python3
"""
Test script to verify the simulation autowiring works correctly.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def test_simulation_autowire():
    """Test the simulation autowiring functionality"""
    print("🧪 Testing Simulation Autowiring")
    print("=" * 50)
    
    try:
        # Import required modules
        from core.base_classes import World, Zone
        from core.enums import ZoneType, NetworkType
        from core.network import Network
        from quantum_network.interactive_host import InteractiveQuantumHost
        from quantum_network.adapter import QuantumAdapter
        
        # Create a simple world and zone
        world = World(size=(100, 100))
        zone = Zone(
            size=(50, 50), 
            position=(0, 0), 
            zone_type=ZoneType.SECURE, 
            parent_zone=world, 
            name="TestZone"
        )
        
        # Create networks
        quantum_network = Network(NetworkType.QUANTUM_NETWORK, world)
        classical_network = Network(NetworkType.CLASSICAL_NETWORK, world)
        
        print("✅ World, zone, and networks created")
        
        # Test 1: Create host and check autowiring
        print("\n🔍 Test 1: Create host and check autowiring")
        host = InteractiveQuantumHost(
            address="test_host",
            location=(10, 10),
            network=quantum_network,
            zone=zone,
            name="Alice"
        )
        
        print(f"   Student code validated: {host.student_code_validated}")
        print(f"   Has student implementation: {host.student_implementation is not None}")
        
        if host.student_implementation:
            print(f"   Student implementation type: {type(host.student_implementation).__name__}")
        
        # Test 2: Test QKD initiation directly on host
        print("\n🔍 Test 2: Test QKD initiation directly on host")
        try:
            # Test if the host can perform QKD
            if host.student_code_validated:
                print("✅ Host is ready for QKD - student implementation validated!")
                
                # Test the BB84 methods directly
                print("\n🔍 Test 3: Test BB84 methods directly")
                
                # Test bb84_send_qubits
                result = host.bb84_send_qubits(5)
                print(f"✅ bb84_send_qubits returned: {result}")
                
                # Test process_received_qbit
                result = host.process_received_qbit("test_qubit", None)
                print(f"✅ process_received_qbit returned: {result}")
                
                # Test bb84_reconcile_bases
                result = host.bb84_reconcile_bases(['Z', 'X', 'Z', 'X', 'Z'])
                print(f"✅ bb84_reconcile_bases returned: {result}")
                
                # Test bb84_estimate_error_rate
                result = host.bb84_estimate_error_rate([(0, 0), (1, 1)])
                print(f"✅ bb84_estimate_error_rate returned: {result}")
                
            else:
                print("❌ Host is not ready for QKD - student implementation not validated")
                return False
                
        except Exception as e:
            print(f"❌ QKD test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ All simulation autowiring tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simulation_autowire()
    sys.exit(0 if success else 1)
