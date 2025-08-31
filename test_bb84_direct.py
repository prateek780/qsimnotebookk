#!/usr/bin/env python3
"""
Direct BB84 Test
================
Test the student BB84 implementation directly
"""

import sys
sys.path.append('.')

from quantum_network.interactive_host import InteractiveQuantumHost
from quantum_network.notebook_bridge import NotebookIntegration, check_simulation_readiness
from quantum_network.channel import QuantumChannel
from core.network import Network
from core.enums import NetworkType

def test_bb84_direct():
    print("🧪 DIRECT BB84 TEST")
    print("="*40)
    
    # Check readiness
    readiness = check_simulation_readiness()
    print(f"Student implementation ready: {readiness['ready']}")
    
    if not readiness['ready']:
        print("❌ Student implementation not ready")
        return False
    
    # Load student implementation
    integration = NotebookIntegration()
    alice_bridge = integration.load_student_implementation()
    bob_bridge = integration.load_student_implementation()
    
    if not alice_bridge or not bob_bridge:
        print("❌ Failed to load student implementations")
        return False
    
    # Create network
    network = Network(network_type=NetworkType.QUANTUM_NETWORK, location=(0, 0), name="Test Network")
    
    # Create hosts
    alice = InteractiveQuantumHost(
        address="alice_test",
        location=(0, 0),
        network=network,
        name="Alice Test",
        student_implementation=alice_bridge
    )
    
    bob = InteractiveQuantumHost(
        address="bob_test",
        location=(10, 0),
        network=network,
        name="Bob Test",
        student_implementation=bob_bridge
    )
    
    # Set up classical communication
    alice.send_classical_data = lambda x: bob.receive_classical_data(x)
    bob.send_classical_data = lambda x: alice.receive_classical_data(x)
    
    # Add to network
    network.add_hosts(alice)
    network.add_hosts(bob)
    
    # Create quantum channel
    channel = QuantumChannel(
        node_1=alice,
        node_2=bob,
        length=10,
        loss_per_km=0,
        noise_model="none",
        name="Test Channel",
        num_bits=20
    )
    
    alice.add_quantum_channel(channel)
    bob.add_quantum_channel(channel)
    
    print("✅ Network and hosts created")
    print(f"Alice implementation: {alice.student_implementation}")
    print(f"Bob implementation: {bob.student_implementation}")
    print(f"Alice validation: {alice.student_code_validated}")
    print(f"Bob validation: {bob.student_code_validated}")
    
    # Test BB84 sending
    print("\n🔬 Testing BB84 sending...")
    alice_result = alice.bb84_send_qubits(20)
    print(f"Alice bb84_send_qubits result: {alice_result}")
    
    # Check Alice's state
    print(f"Alice basis choices: {len(getattr(alice, 'basis_choices', []))}")
    print(f"Alice measurement outcomes: {len(getattr(alice, 'measurement_outcomes', []))}")
    
    # Process quantum buffer
    print("\n🔄 Processing quantum communications...")
    for i in range(50):
        if not bob.qmemeory_buffer.empty():
            print(f"Step {i}: Bob has {bob.qmemeory_buffer.qsize()} qubits in buffer")
            bob.forward()
        
        if bob.qmemeory_buffer.empty():
            break
    
    # Check Bob's state
    print(f"Bob basis choices: {len(getattr(bob, 'basis_choices', []))}")
    print(f"Bob measurement outcomes: {len(getattr(bob, 'measurement_outcomes', []))}")
    
    # Test reconciliation
    if len(getattr(bob, 'measurement_outcomes', [])) > 0:
        print("\n🔄 Testing basis reconciliation...")
        bob.send_bases_for_reconcile()
        
        # Let classical messages propagate
        for i in range(10):
            # Process any remaining quantum/classical communications
            if not alice.qmemeory_buffer.empty():
                alice.forward()
            if not bob.qmemeory_buffer.empty():
                bob.forward()
    
    # Final state
    alice_measurements = len(getattr(alice, 'measurement_outcomes', []))
    bob_measurements = len(getattr(bob, 'measurement_outcomes', []))
    alice_shared = len(getattr(alice, 'shared_bases_indices', []))
    bob_shared = len(getattr(bob, 'shared_bases_indices', []))
    
    print(f"\n📊 Final Results:")
    print(f"Alice measurements: {alice_measurements}")
    print(f"Bob measurements: {bob_measurements}")
    print(f"Alice shared indices: {alice_shared}")
    print(f"Bob shared indices: {bob_shared}")
    
    success = alice_measurements > 0 and bob_measurements > 0
    print(f"\n{'✅' if success else '❌'} BB84 Test {'PASSED' if success else 'FAILED'}")
    
    return success

if __name__ == "__main__":
    test_bb84_direct()
