#!/usr/bin/env python3
"""
Complete Quantum Network Simulation with Student BB84 Implementation
===================================================================

This script runs the complete quantum network simulation using student-implemented
BB84 algorithms from the Jupyter notebook. It integrates quantum key distribution
with classical networking, encryption, and message passing.

Usage:
    python complete_simulation.py

Prerequisites:
    1. Students must complete BB84 implementation in quantum_networking_complete.ipynb
    2. Students must export their implementation using the notebook bridge
    3. student_implementation_status.json must exist and show implementation is ready
"""

import time
import sys
import json
import os
import random
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.append('.')

try:
    from core.base_classes import World, Zone
    from core.enums import NetworkType, ZoneType
    from core.network import Network
    from quantum_network.interactive_host import InteractiveQuantumHost
    from quantum_network.channel import QuantumChannel
    from quantum_network.notebook_bridge import NotebookIntegration, check_simulation_readiness
    from classical_network.connection import ClassicConnection
    from classical_network.host import ClassicalHost
    from classical_network.router import ClassicalRouter
    from classical_network.presets.connection_presets import DEFAULT_PRESET
    from utils.quantum_encryption import quantum_xor_encrypt, quantum_xor_decrypt
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class QuantumNetworkSimulation:
    """Complete quantum network simulation with student BB84 implementation"""
    
    def __init__(self):
        self.world = None
        self.alice_classical = None
        self.bob_classical = None
        self.alice_quantum = None
        self.bob_quantum = None
        self.shared_keys = {}
        self.messages_sent = []
        self.simulation_results = {}
        
        print("🌐 Quantum Network Simulation Initialized")
        print("   Ready to run complete simulation with student BB84 code!")
    
    def check_student_implementation(self) -> bool:
        """Check if student implementation is ready"""
        readiness = check_simulation_readiness()
        
        if not readiness["ready"]:
            print(f"❌ Simulation not ready: {readiness['reason']}")
            print("\n💡 To fix this:")
            print("1. Open quantum_networking_complete.ipynb")
            print("2. Complete all BB84 implementation cells")
            print("3. Run the 'Export Implementation' cell")
            print("4. Re-run this simulation")
            return False
        
        print("✅ Student BB84 implementation verified!")
        print(f"   Status: {readiness['status']}")
        return True
    
    def setup_world(self):
        """Create the simulation world with zones"""
        print("\n🌍 Setting up simulation world...")
        
        # Create main world
        self.world = World(size=(200, 200), name="Student Quantum Network World")
        
        # Create classical networking zone
        classical_zone = Zone(
            size=(80, 80),
            position=(10, 60),
            zone_type=ZoneType.SECURE,
            parent_zone=self.world,
            name="Classical Network Zone"
        )
        self.world.add_zone(classical_zone)
        
        # Create quantum networking zone
        quantum_zone = Zone(
            size=(80, 80),
            position=(110, 60),
            zone_type=ZoneType.SECURE,
            parent_zone=self.world,
            name="Quantum Network Zone"
        )
        self.world.add_zone(quantum_zone)
        
        print("✅ World and zones created")
        return classical_zone, quantum_zone
    
    def setup_classical_network(self, classical_zone):
        """Set up classical network infrastructure"""
        print("\n🔌 Setting up classical network...")
        
        # Create classical network
        classical_net = Network(
            network_type=NetworkType.CLASSICAL_NETWORK,
            location=(0, 0),
            zone=classical_zone,
            name="Classical Network"
        )
        classical_zone.add_network(classical_net)
        
        # Create classical hosts
        self.alice_classical = ClassicalHost(
            address="192.168.1.10",
            location=(20, 20),
            network=classical_net,
            zone=classical_zone,
            name="Alice Classical"
        )
        
        self.bob_classical = ClassicalHost(
            address="192.168.1.20",
            location=(60, 20),
            network=classical_net,
            zone=classical_zone,
            name="Bob Classical"
        )
        
        # Create router
        router = ClassicalRouter(
            address="192.168.1.1",
            location=(40, 40),
            network=classical_net,
            zone=classical_zone,
            name="Classical Router"
        )
        
        # Add hosts to network
        classical_net.add_hosts(self.alice_classical)
        classical_net.add_hosts(self.bob_classical)
        classical_net.add_hosts(router)
        
        # Create connections
        alice_router_conn = ClassicConnection(
            node_1=self.alice_classical,
            node_2=router,
            config=DEFAULT_PRESET,
            name="Alice-Router Connection"
        )
        
        router_bob_conn = ClassicConnection(
            node_1=router,
            node_2=self.bob_classical,
            config=DEFAULT_PRESET,
            name="Router-Bob Connection"
        )
        
        # Add connections
        self.alice_classical.add_connection(alice_router_conn)
        router.add_connection(alice_router_conn)
        router.add_connection(router_bob_conn)
        self.bob_classical.add_connection(router_bob_conn)
        
        print("✅ Classical network infrastructure ready")
        return classical_net
    
    def setup_quantum_network(self, quantum_zone):
        """Set up quantum network with student implementation"""
        print("\n🔬 Setting up quantum network with student BB84 implementation...")
        
        # Create quantum network
        quantum_net = Network(
            network_type=NetworkType.QUANTUM_NETWORK,
            location=(0, 0),
            zone=quantum_zone,
            name="Student Quantum Network"
        )
        quantum_zone.add_network(quantum_net)
        
        # Load student implementation
        integration = NotebookIntegration()
        student_bridge = integration.load_student_implementation()
        
        if not student_bridge:
            raise RuntimeError("Failed to load student BB84 implementation")
        
        # Create quantum hosts with student implementation
        self.alice_quantum = InteractiveQuantumHost(
            address="q_alice",
            location=(20, 20),
            network=quantum_net,
            zone=quantum_zone,
            name="Alice Quantum",
            student_implementation=student_bridge,
            qkd_completed_fn=lambda key: self.on_qkd_completed("alice", key)
        )
        
        bob_bridge = integration.load_student_implementation()
        self.bob_quantum = InteractiveQuantumHost(
            address="q_bob",
            location=(60, 20),
            network=quantum_net,
            zone=quantum_zone,
            name="Bob Quantum",
            student_implementation=bob_bridge,
            qkd_completed_fn=lambda key: self.on_qkd_completed("bob", key)
        )
        
        # Set up classical communication between quantum hosts
        self.alice_quantum.send_classical_data = lambda x: self.bob_quantum.receive_classical_data(x)
        self.bob_quantum.send_classical_data = lambda x: self.alice_quantum.receive_classical_data(x)
        
        # Add hosts to network
        quantum_net.add_hosts(self.alice_quantum)
        quantum_net.add_hosts(self.bob_quantum)
        
        # Create quantum channel with minimal loss for demonstration
        quantum_channel = QuantumChannel(
            node_1=self.alice_quantum,
            node_2=self.bob_quantum,
            length=1,  # Short distance to minimize loss
            loss_per_km=0.001,  # Very low loss rate
            noise_model="none",  # No noise for clean demonstration
            name="Alice-Bob Quantum Channel",
            num_bits=50  # Reasonable number of qubits for BB84
        )
        
        # Add channel to hosts
        self.alice_quantum.add_quantum_channel(quantum_channel)
        self.bob_quantum.add_quantum_channel(quantum_channel)
        
        print("✅ Quantum network with student BB84 implementation ready")
        return quantum_net
    
    def on_qkd_completed(self, host_name: str, shared_key: List[int]):
        """Callback when QKD is completed"""
        self.shared_keys[host_name] = shared_key
        print(f"🔑 {host_name.title()} completed QKD - Key length: {len(shared_key)} bits")
        print(f"   Key sample: {shared_key[:10]}..." if len(shared_key) > 10 else f"   Full key: {shared_key}")
        
        # Check if both hosts have completed QKD
        if len(self.shared_keys) == 2:
            self.demonstrate_secure_communication()
    
    def run_bb84_protocol(self):
        """Run the BB84 quantum key distribution protocol"""
        print("\n🔬 Starting BB84 Quantum Key Distribution...")
        print("   Using student-implemented BB84 algorithms!")
        
        # Start BB84 from Alice
        print("   Alice initiating BB84 protocol...")
        
        # Debug: Check channel setup
        alice_channel = self.alice_quantum.get_channel()
        bob_channel = self.bob_quantum.get_channel()
        print(f"   Alice channel: {alice_channel}")
        print(f"   Bob channel: {bob_channel}")
        
        # Debug: Check if student implementation is properly attached
        alice_impl = getattr(self.alice_quantum, 'student_implementation', None)
        bob_impl = getattr(self.bob_quantum, 'student_implementation', None)
        print(f"   Alice implementation: {alice_impl}")
        print(f"   Bob implementation: {bob_impl}")
        
        # Start the protocol
        result = self.alice_quantum.perform_qkd()
        print(f"   Alice perform_qkd result: {result}")
        
        # Manual trigger if needed
        if alice_channel:
            print(f"   Channel details: {alice_channel.name}, nodes: {alice_channel.node_1.name} <-> {alice_channel.node_2.name}")
            # Try calling bb84_send_qubits directly
            alice_result = self.alice_quantum.bb84_send_qubits(50)
            print(f"   Direct bb84_send_qubits result: {alice_result}")
        
        # Process quantum communications
        print("   Processing quantum communications...")
        for i in range(500):  # Allow time for quantum processing
            try:
                # Process quantum memory buffers
                alice_processed = False
                bob_processed = False
                
                if not self.alice_quantum.qmemeory_buffer.empty():
                    self.alice_quantum.forward()
                    alice_processed = True
                
                if not self.bob_quantum.qmemeory_buffer.empty():
                    self.bob_quantum.forward()
                    bob_processed = True
                
                # Show progress every 50 iterations
                if i % 50 == 0:
                    print(f"   Step {i}: Alice buffer size: {self.alice_quantum.qmemeory_buffer.qsize()}, Bob buffer size: {self.bob_quantum.qmemeory_buffer.qsize()}")
                    print(f"   Alice measurements: {len(getattr(self.alice_quantum, 'measurement_outcomes', []))}, Bob measurements: {len(getattr(self.bob_quantum, 'measurement_outcomes', []))}")
                
                time.sleep(0.01)
                
                # Check if both sides have completed
                if len(self.shared_keys) == 2:
                    print("   Both parties completed QKD!")
                    break
                
                # Check if we have measurements but no shared keys yet
                alice_measurements = len(getattr(self.alice_quantum, 'measurement_outcomes', []))
                bob_measurements = len(getattr(self.bob_quantum, 'measurement_outcomes', []))
                
                if alice_measurements > 0 and bob_measurements > 0 and i > 100:
                    print(f"   Measurements exist but QKD not completing. Alice: {alice_measurements}, Bob: {bob_measurements}")
                    if i > 200:  # Give up after reasonable time
                        print("   Timeout - QKD protocol not completing properly")
                        break
                    
            except Exception as e:
                print(f"   Processing step {i} error: {e}")
                continue
        
        # Verify QKD completion
        if len(self.shared_keys) == 2:
            alice_key = self.shared_keys.get("alice", [])
            bob_key = self.shared_keys.get("bob", [])
            
            if alice_key == bob_key:
                print("✅ BB84 Protocol completed successfully!")
                print(f"   Shared key established: {len(alice_key)} bits")
                return True
            else:
                print("⚠️ BB84 completed but keys don't match!")
                print(f"   Alice key length: {len(alice_key)}")
                print(f"   Bob key length: {len(bob_key)}")
                return False
        else:
            print("❌ BB84 Protocol did not complete")
            return False
    
    def demonstrate_secure_communication(self):
        """Demonstrate secure communication using the shared quantum key"""
        print("\n🔒 Demonstrating Secure Communication...")
        
        if len(self.shared_keys) != 2:
            print("❌ Cannot demonstrate secure communication - QKD not completed")
            return
        
        alice_key = self.shared_keys["alice"]
        bob_key = self.shared_keys["bob"]
        
        if alice_key != bob_key:
            print("❌ Keys don't match - insecure!")
            return
        
        # Convert key to bytes for encryption
        key_bytes = bytes([bit for bit in alice_key[:32]])  # Use first 32 bits as key
        
        # Demonstrate message encryption and decryption
        messages = [
            "Hello Bob! This message is quantum-encrypted! 🔐",
            "The BB84 protocol worked perfectly! 🎉",
            "Quantum cryptography is amazing! ⚛️"
        ]
        
        print("📨 Sending encrypted messages...")
        for i, message in enumerate(messages, 1):
            print(f"\n   Message {i}: {message}")
            
            # Encrypt with quantum key
            encrypted, metadata = quantum_xor_encrypt(message, alice_key[:len(message)*8])
            print(f"   Encrypted: {encrypted.hex()}")
            
            # Bob decrypts
            decrypted = quantum_xor_decrypt(encrypted, bob_key[:len(message)*8], metadata)
            print(f"   Decrypted: {decrypted}")
            
            # Verify
            if decrypted == message:
                print("   ✅ Message transmitted securely!")
            else:
                print("   ❌ Decryption failed!")
            
            self.messages_sent.append({
                "original": message,
                "encrypted": encrypted.hex(),
                "decrypted": decrypted,
                "success": decrypted == message
            })
    
    def generate_simulation_report(self):
        """Generate a comprehensive simulation report"""
        print("\n📊 Generating Simulation Report...")
        
        # Collect statistics
        alice_stats = self.alice_quantum.get_learning_stats() if self.alice_quantum else {}
        bob_stats = self.bob_quantum.get_learning_stats() if self.bob_quantum else {}
        
        report = {
            "simulation_name": "Complete Quantum Network with Student BB84",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "qkd_results": {
                "completed": len(self.shared_keys) == 2,
                "alice_key_length": len(self.shared_keys.get("alice", [])),
                "bob_key_length": len(self.shared_keys.get("bob", [])),
                "keys_match": self.shared_keys.get("alice", []) == self.shared_keys.get("bob", [])
            },
            "communication_results": {
                "messages_sent": len(self.messages_sent),
                "successful_transmissions": sum(1 for msg in self.messages_sent if msg["success"]),
                "encryption_success_rate": (sum(1 for msg in self.messages_sent if msg["success"]) / 
                                          max(1, len(self.messages_sent))) * 100
            },
            "learning_statistics": {
                "alice": alice_stats,
                "bob": bob_stats
            }
        }
        
        # Save report
        with open("simulation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        print("\n" + "="*60)
        print("🎯 SIMULATION COMPLETE - RESULTS SUMMARY")
        print("="*60)
        print(f"✅ QKD Completed: {report['qkd_results']['completed']}")
        print(f"🔑 Shared Key Length: {report['qkd_results']['alice_key_length']} bits")
        print(f"🔒 Keys Match: {report['qkd_results']['keys_match']}")
        print(f"📨 Messages Sent: {report['communication_results']['messages_sent']}")
        print(f"🎯 Success Rate: {report['communication_results']['encryption_success_rate']:.1f}%")
        print(f"📊 Report saved to: simulation_report.json")
        print("="*60)
        
        return report
    
    def run_complete_simulation(self):
        """Run the complete quantum network simulation"""
        print("\n🚀 STARTING COMPLETE QUANTUM NETWORK SIMULATION")
        print("="*60)
        print("   Integration: Jupyter Notebook ↔ Quantum Simulation")
        print("   Protocol: Student-Implemented BB84 + Secure Messaging")
        print("="*60)
        
        try:
            # Step 1: Check student implementation
            if not self.check_student_implementation():
                return False
            
            # Step 2: Setup simulation world
            classical_zone, quantum_zone = self.setup_world()
            
            # Step 3: Setup classical network
            self.setup_classical_network(classical_zone)
            
            # Step 4: Setup quantum network
            self.setup_quantum_network(quantum_zone)
            
            # Step 5: Run BB84 protocol
            bb84_success = self.run_bb84_protocol()
            
            if not bb84_success:
                print("❌ BB84 protocol failed - cannot proceed with secure communication")
                return False
            
            # Step 6: Wait for secure communication demonstration
            # (This is triggered automatically by QKD completion)
            time.sleep(2)
            
            # Step 7: Generate report
            self.generate_simulation_report()
            
            print("\n🎉 SIMULATION COMPLETED SUCCESSFULLY!")
            print("   Students have successfully implemented BB84 and achieved secure communication!")
            
            return True
            
        except Exception as e:
            print(f"❌ Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point for the complete simulation"""
    print("🌐 Complete Quantum Network Simulation")
    print("   Student BB84 Implementation + Full Network Integration")
    print()
    
    # Create and run simulation
    simulation = QuantumNetworkSimulation()
    success = simulation.run_complete_simulation()
    
    if success:
        print("\n✅ All systems operational!")
        print("🎓 Students have mastered quantum networking!")
    else:
        print("\n❌ Simulation incomplete")
        print("💡 Check student implementation and try again")
    
    return success


if __name__ == "__main__":
    main()
