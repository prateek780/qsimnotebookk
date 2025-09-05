#!/usr/bin/env python3
"""
Test script to run just the QKD part without the full simulation.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def test_qkd_only():
    """Test just the QKD functionality"""
    print("🧪 Testing QKD Only")
    print("=" * 50)
    
    try:
        # Import required modules
        from core.base_classes import World, Zone
        from core.enums import ZoneType, NetworkType
        from core.network import Network
        from quantum_network.interactive_host import InteractiveQuantumHost
        from quantum_network.adapter import QuantumAdapter
        from quantum_network.channel import QuantumChannel
        
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
        
        # Create quantum hosts
        print("\n🔍 Creating quantum hosts...")
        alice = InteractiveQuantumHost(
            address="alice",
            location=(10, 10),
            network=quantum_network,
            zone=zone,
            name="Alice"
        )
        
        bob = InteractiveQuantumHost(
            address="bob",
            location=(40, 10),
            network=quantum_network,
            zone=zone,
            name="Bob"
        )
        
        print(f"   Alice student code validated: {alice.student_code_validated}")
        print(f"   Bob student code validated: {bob.student_code_validated}")
        
        # Create quantum channel
        print("\n🔍 Creating quantum channel...")
        channel = QuantumChannel(
            node_1=alice,
            node_2=bob,
            length=30,
            loss_per_km=0,
            noise_model="simple",
            name="Alice-Bob Channel",
            num_bits=50
        )
        
        # Add the channel to both hosts
        alice.add_quantum_channel(channel)
        bob.add_quantum_channel(channel)
        
        print("✅ Quantum channel created and connected to hosts")
        
        # Create adapters
        print("\n🔍 Creating adapters...")
        
        # Create adapters without paired adapters first
        adapter1 = QuantumAdapter(
            address="adapter1",
            classical_network=classical_network,
            quantum_network=quantum_network,
            location=(20, 20),
            paired_adapter=None,  # Set to None initially
            quantum_host=alice,
            zone=zone,
            name="Adapter1"
        )
        
        adapter2 = QuantumAdapter(
            address="adapter2",
            classical_network=classical_network,
            quantum_network=quantum_network,
            location=(30, 20),
            paired_adapter=None,  # Set to None initially
            quantum_host=bob,
            zone=zone,
            name="Adapter2"
        )
        
        # Now pair them
        adapter1.add_paired_adapter(adapter2)
        adapter2.add_paired_adapter(adapter1)
        
        print("✅ Adapters created")
        
        # Test QKD initiation
        print("\n🔍 Testing QKD initiation...")
        try:
            adapter1.initiate_qkd()
            print("✅ QKD initiation successful!")
        except Exception as e:
            print(f"❌ QKD initiation failed: {e}")
            return False
        
        print("\n✅ All QKD tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qkd_only()
    sys.exit(0 if success else 1)
