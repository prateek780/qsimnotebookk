#!/usr/bin/env python3
"""
Standalone Student BB84 Simulation
==================================

This script runs a complete BB84 simulation using student implementation
without any server-side dependencies. Perfect for educational use.
"""

import sys
import time
import random
from typing import List

# Add current directory to path
sys.path.append('.')

def run_standalone_bb84_simulation():
    """Run BB84 simulation without server dependencies"""
    print("🌐 STANDALONE QUANTUM BB84 SIMULATION")
    print("="*60)
    print("🎓 Using YOUR BB84 implementation from notebook!")
    print("🔬 Running complete quantum key distribution protocol")
    print("="*60)
    
    try:
        # Import only what we need, avoid server dependencies
        from quantum_network.interactive_host import InteractiveQuantumHost
        from quantum_network.notebook_bridge import NotebookIntegration, check_simulation_readiness
        from quantum_network.channel import QuantumChannel
        from core.network import Network
        from core.enums import NetworkType
        from utils.quantum_encryption import quantum_xor_encrypt, quantum_xor_decrypt
        
        # Check student implementation
        readiness = check_simulation_readiness()
        if not readiness['ready']:
            print(f"❌ Student implementation not ready: {readiness.get('reason', 'Unknown')}")
            return False
        
        print("✅ Student BB84 implementation verified!")
        
        # Load student implementations
        integration = NotebookIntegration()
        alice_bridge = integration.load_student_implementation()
        bob_bridge = integration.load_student_implementation()
        
        if not alice_bridge or not bob_bridge:
            print("❌ Failed to load student implementations")
            return False
        
        # Create quantum network
        network = Network(network_type=NetworkType.QUANTUM_NETWORK, location=(0, 0), name="Student BB84 Network")
        
        # Track shared keys
        shared_keys = {}
        
        def on_qkd_completed(host_name: str, key: List[int]):
            shared_keys[host_name] = key
            print(f"🔑 {host_name.title()} completed QKD - Key length: {len(key)} bits")
            if len(key) > 10:
                print(f"   Key sample: {key[:10]}...")
            else:
                print(f"   Full key: {key}")
        
        # Create quantum hosts
        alice = InteractiveQuantumHost(
            address="alice_standalone",
            location=(0, 0),
            network=network,
            name="Alice",
            student_implementation=alice_bridge,
            qkd_completed_fn=lambda key: on_qkd_completed("alice", key)
        )
        
        bob = InteractiveQuantumHost(
            address="bob_standalone",
            location=(10, 0),
            network=network,
            name="Bob",
            student_implementation=bob_bridge,
            qkd_completed_fn=lambda key: on_qkd_completed("bob", key)
        )
        
        # Set up classical communication
        alice.send_classical_data = lambda x: bob.receive_classical_data(x)
        bob.send_classical_data = lambda x: alice.receive_classical_data(x)
        
        # Add hosts to network
        network.add_hosts(alice)
        network.add_hosts(bob)
        
        # Create quantum channel with no loss for clean demonstration
        channel = QuantumChannel(
            node_1=alice,
            node_2=bob,
            length=0.1,  # Very short distance
            loss_per_km=0.0,  # No loss
            noise_model="none",  # No noise
            name="Alice-Bob Direct Channel",
            num_bits=50
        )
        
        alice.add_quantum_channel(channel)
        bob.add_quantum_channel(channel)
        
        print("✅ Quantum network created successfully!")
        print(f"   Network: {network.name}")
        print(f"   Hosts: {alice.name} ↔ {bob.name}")
        print(f"   Channel: {channel.name} (no loss, no noise)")
        
        # Run BB84 protocol
        print("\n🔬 Starting BB84 Quantum Key Distribution...")
        print("   Alice initiating protocol...")
        
        # Start BB84
        alice.perform_qkd()
        
        # Process quantum communications
        print("   Processing quantum communications...")
        max_iterations = 200
        for i in range(max_iterations):
            # Process quantum buffers
            alice_processed = False
            bob_processed = False
            
            if not alice.qmemeory_buffer.empty():
                alice.forward()
                alice_processed = True
            
            if not bob.qmemeory_buffer.empty():
                bob.forward()
                bob_processed = True
            
            # Show progress
            if i % 25 == 0:
                alice_measurements = len(getattr(alice, 'measurement_outcomes', []))
                bob_measurements = len(getattr(bob, 'measurement_outcomes', []))
                print(f"   Step {i}: Alice: {alice_measurements}, Bob: {bob_measurements}")
            
            # Check completion
            if len(shared_keys) == 2:
                print("   Both parties completed QKD!")
                break
            
            # Small delay
            time.sleep(0.01)
        
        # Verify results
        if len(shared_keys) == 2:
            alice_key = shared_keys.get("alice", [])
            bob_key = shared_keys.get("bob", [])
            
            # Debug key comparison
            print(f"\n🔍 Key Comparison Debug:")
            print(f"   Alice key: {alice_key[:10]}..." if len(alice_key) > 10 else f"   Alice key: {alice_key}")
            print(f"   Bob key:   {bob_key[:10]}..." if len(bob_key) > 10 else f"   Bob key:   {bob_key}")
            print(f"   Keys match: {alice_key == bob_key}")
            
            if alice_key == bob_key and len(alice_key) > 0:
                print("\n🎉 BB84 PROTOCOL SUCCESSFUL!")
                print(f"✅ Shared key established: {len(alice_key)} bits")
                print(f"✅ Keys match perfectly!")
                
                # Demonstrate secure messaging
                print("\n🔐 Demonstrating Secure Messaging...")
                messages = [
                    "Hello Bob! This is quantum-secured! 🔐",
                    "BB84 protocol worked perfectly! ⚛️",
                    "Quantum cryptography is amazing! 🎉"
                ]
                
                for i, message in enumerate(messages, 1):
                    print(f"\n📨 Message {i}: {message}")
                    
                    # Use first part of key for encryption
                    key_bits_needed = len(message) * 8
                    if len(alice_key) >= key_bits_needed:
                        encrypted, metadata = quantum_xor_encrypt(message, alice_key[:key_bits_needed])
                        print(f"🔒 Encrypted: {encrypted.hex()}")
                        
                        decrypted = quantum_xor_decrypt(encrypted, bob_key[:key_bits_needed], metadata)
                        print(f"🔓 Decrypted: {decrypted}")
                        
                        if message == decrypted:
                            print("✅ Message transmitted securely!")
                        else:
                            print("❌ Decryption failed!")
                    else:
                        print("⚠️ Not enough key material for this message")
                
                # Generate summary
                print("\n📊 SIMULATION SUMMARY")
                print("="*40)
                print(f"✅ BB84 Protocol: SUCCESS")
                print(f"🔑 Shared Key Length: {len(alice_key)} bits")
                print(f"🔒 Secure Messages: {len(messages)}")
                print(f"⚛️ Student Implementation: WORKING")
                print(f"🎓 Quantum Networking: MASTERED")
                print("="*40)
                
                return True
            else:
                print("\n❌ Keys don't match or are empty!")
                print(f"Alice key length: {len(alice_key)}")
                print(f"Bob key length: {len(bob_key)}")
                return False
        else:
            print("\n❌ BB84 protocol did not complete")
            print(f"Shared keys received: {len(shared_keys)}")
            return False
            
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    print("🎓 Student BB84 Quantum Simulation")
    print("   Standalone version - no server dependencies")
    print()
    
    success = run_standalone_bb84_simulation()
    
    if success:
        print("\n🎊 CONGRATULATIONS!")
        print("You have successfully implemented and run BB84!")
        print("Your quantum networking skills are now complete! 🌟")
    else:
        print("\n💡 If the simulation didn't work:")
        print("1. Make sure you exported your implementation from the notebook")
        print("2. Check that student_implementation_status.json exists")
        print("3. Verify all BB84 methods are implemented")
    
    return success

if __name__ == "__main__":
    main()
