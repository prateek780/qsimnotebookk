# 🚀 COMPLETE QUANTUM-CLASSICAL NETWORK SIMULATION IN NOTEBOOK
# ================================================================
# This cell runs the complete simulation using your student BB84 implementation
# It includes: Classical hosts → Quantum adapters → BB84 protocol → Secure messaging

import sys
import time
import random
from IPython.display import display, HTML

# Add current directory to path for imports
import os
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

def check_student_bb84_implementation():
    """
    CRITICAL: Check if student has completed their BB84 implementation.
    Returns True only if StudentQuantumHost class exists with all required methods.
    """
    print("🔍 Checking for student BB84 implementation...")
    
    try:
        # Check if StudentQuantumHost class is defined in the current scope
        import sys
        current_frame = sys._getframe(1)
        global_vars = current_frame.f_globals
        
        if 'StudentQuantumHost' not in global_vars:
            print("❌ StudentQuantumHost class not found!")
            return False
        
        # Get the class and verify it has all required methods
        StudentQuantumHost = global_vars['StudentQuantumHost']
        required_methods = ['bb84_send_qubits', 'process_received_qbit', 'bb84_reconcile_bases', 'bb84_estimate_error_rate']
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(StudentQuantumHost, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ StudentQuantumHost missing methods: {missing_methods}")
            return False
        
        # Test that we can create an instance
        try:
            test_instance = StudentQuantumHost("Test")
            print("✅ StudentQuantumHost class found with all required methods!")
            return True
        except Exception as e:
            print(f"❌ Error creating StudentQuantumHost instance: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking student implementation: {e}")
        return False

def run_complete_simulation_in_notebook():
    """
    Run the complete quantum-classical simulation that matches your original output.
    This integrates classical message passing with quantum BB84 protocol.
    """
    print("🌐 COMPLETE QUANTUM NETWORK SIMULATION")
    print("=" * 60)
    print("🎓 Using YOUR student BB84 implementation!")
    print("🔗 Classical Network + Quantum Adapters + BB84 Protocol")
    print("=" * 60)
    
    # Check if status file exists first
    def _check_status_file_exists():
        try:
            import os
            import json
            status_file = "student_implementation_status.json"
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    status = json.load(f)
                    return status.get("student_implementation_ready", False)
            return False
        except Exception:
            return False
    
    # CRITICAL: Check if student has completed their BB84 vibe code
    if not _check_status_file_exists() and not check_student_bb84_implementation():
        print("\n" + "=" * 80)
        print("🚫 SIMULATION BLOCKED - STUDENT BB84 IMPLEMENTATION REQUIRED!")
        print("=" * 80)
        print("❌ You must complete your BB84 algorithm to run this simulation!")
        print("")
        print("📝 VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION")
        print("")
        print("🔧 Steps to enable the simulation:")
        print("1. Complete the StudentQuantumHost class in the notebook")
        print("2. Implement all required methods:")
        print("   - bb84_send_qubits()")
        print("   - process_received_qbit()")
        print("   - bb84_reconcile_bases()")
        print("   - bb84_estimate_error_rate()")
        print("3. Run the notebook cells to define the class")
        print("4. Then run this simulation")
        print("")
        print("🎯 The simulation will ONLY work with your completed BB84 implementation!")
        print("=" * 80)
        return False
    
    try:
        # Import all required modules
        from classical_network.connection import ClassicConnection
        from classical_network.host import ClassicalHost
        from classical_network.router import ClassicalRouter
        from core.base_classes import World, Zone
        from core.enums import NetworkType, ZoneType
        from core.network import Network
        from quantum_network.adapter import QuantumAdapter
        from quantum_network.channel import QuantumChannel
        from quantum_network.interactive_host import InteractiveQuantumHost
        from classical_network.presets.connection_presets import DEFAULT_PRESET
        
        print("✅ All modules imported successfully")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the correct directory")
        return False
    
    # Step 1: Create World and Zones
    print("\n🌍 Step 1: Creating world and zones...")
    world = World(size=(200, 200), name="Complete Simulation World")
    
    # Classical zones
    classical_zone1 = Zone(
        size=(80, 80), position=(10, 100), zone_type=ZoneType.SECURE,
        parent_zone=world, name="Classical Zone 1"
    )
    classical_zone2 = Zone(
        size=(80, 80), position=(100, 100), zone_type=ZoneType.SECURE,
        parent_zone=world, name="Classical Zone 2"
    )
    quantum_zone = Zone(
        size=(80, 80), position=(50, 10), zone_type=ZoneType.SECURE,
        parent_zone=world, name="Quantum Zone"
    )
    
    world.add_zone(classical_zone1)
    world.add_zone(classical_zone2)
    world.add_zone(quantum_zone)
    print("✅ World and zones created")
    
    # Step 2: Create Classical Networks
    print("\n🔌 Step 2: Setting up classical networks...")
    
    # Classical Network 1
    classical_net1 = Network(
        network_type=NetworkType.CLASSICAL_NETWORK,
        location=(0, 0), zone=classical_zone1, name="Classical Network 1"
    )
    classical_zone1.add_network(classical_net1)
    
    # Classical hosts and router for network 1
    alice_classical = ClassicalHost(
        address="192.168.1.8", location=(20, 20), network=classical_net1,
        zone=classical_zone1, name="ClassicalHost-8"
    )
    bob_classical = ClassicalHost(
        address="192.168.1.1", location=(60, 20), network=classical_net1,
        zone=classical_zone1, name="ClassicalHost-1"
    )
    router1 = ClassicalRouter(
        address="192.168.1.7", location=(40, 40), network=classical_net1,
        zone=classical_zone1, name="ClassicalRouter-7"
    )
    
    classical_net1.add_hosts(alice_classical)
    classical_net1.add_hosts(bob_classical)
    classical_net1.add_hosts(router1)
    
    # Classical Network 2
    classical_net2 = Network(
        network_type=NetworkType.CLASSICAL_NETWORK,
        location=(0, 0), zone=classical_zone2, name="Classical Network 2"
    )
    classical_zone2.add_network(classical_net2)
    
    # Classical hosts and router for network 2
    charlie_classical = ClassicalHost(
        address="192.168.2.2", location=(20, 20), network=classical_net2,
        zone=classical_zone2, name="ClassicalHost-2"
    )
    dave_classical = ClassicalHost(
        address="192.168.2.3", location=(60, 20), network=classical_net2,
        zone=classical_zone2, name="ClassicalHost-3"
    )
    router2 = ClassicalRouter(
        address="192.168.2.1", location=(40, 40), network=classical_net2,
        zone=classical_zone2, name="ClassicalRouter-2"
    )
    
    classical_net2.add_hosts(charlie_classical)
    classical_net2.add_hosts(dave_classical)
    classical_net2.add_hosts(router2)
    
    # Create classical connections
    for host, router, net_name in [
        (alice_classical, router1, "Net1"), (router1, bob_classical, "Net1"),
        (charlie_classical, router2, "Net2"), (router2, dave_classical, "Net2")
    ]:
        conn = ClassicConnection(host, router, DEFAULT_PRESET, f"{host.name}-{router.name}")
        host.add_connection(conn)
        router.add_connection(conn)
    
    print("✅ Classical networks created")
    
    # Step 3: Create Quantum Network with Student Implementation
    print("\n🔬 Step 3: Setting up quantum network with student BB84...")
    
    quantum_net = Network(
        network_type=NetworkType.QUANTUM_NETWORK,
        location=(0, 0), zone=quantum_zone, name="Student Quantum Network"
    )
    quantum_zone.add_network(quantum_net)
    
    # Load student implementation
    try:
        # Try enhanced bridge first
        from enhanced_student_bridge import StudentImplementationBridge
        print("✅ Using enhanced student bridge")
        
        alice_bridge = StudentImplementationBridge(None)
        dave_bridge = StudentImplementationBridge(None)
        
    except ImportError:
        try:
            # Fallback to standard bridge
            from student_impl_bridge import StudentImplementationBridge
            print("✅ Using standard student bridge")
            
            alice_bridge = StudentImplementationBridge(None)
            dave_bridge = StudentImplementationBridge(None)
            
        except ImportError:
            print("❌ No student implementation bridge found!")
            print("💡 Make sure you've run the notebook cells to create the bridge")
            return False
    
    # Track QKD status
    qkd_status = {'completed': False, 'keys': {}}
    
    def on_alice_qkd(key):
        qkd_status['keys']['alice'] = key
        print(f"🔑 Alice QKD completed: {len(key)} bits")
        check_completion()
    
    def on_dave_qkd(key):
        qkd_status['keys']['dave'] = key
        print(f"🔑 Dave QKD completed: {len(key)} bits")
        check_completion()
    
    def check_completion():
        if 'alice' in qkd_status['keys'] and 'dave' in qkd_status['keys']:
            alice_key = qkd_status['keys']['alice']
            dave_key = qkd_status['keys']['dave']
            if alice_key == dave_key:
                print("🎉 BB84 SUCCESS! Keys match perfectly!")
                qkd_status['completed'] = True
            else:
                print("❌ Key mismatch detected")
    
    # Create quantum hosts
    alice_quantum = InteractiveQuantumHost(
        address="q_alice", location=(30, 30), network=quantum_net, zone=quantum_zone,
        name="QuantumHost-4", student_implementation=alice_bridge,
        qkd_completed_fn=on_alice_qkd
    )
    
    dave_quantum = InteractiveQuantumHost(
        address="q_dave", location=(70, 30), network=quantum_net, zone=quantum_zone,
        name="QuantumHost-5", student_implementation=dave_bridge,
        qkd_completed_fn=on_dave_qkd
    )
    
    # Set up classical communication between quantum hosts
    alice_quantum.send_classical_data = lambda x: dave_quantum.receive_classical_data(x)
    dave_quantum.send_classical_data = lambda x: alice_quantum.receive_classical_data(x)
    
    quantum_net.add_hosts(alice_quantum)
    quantum_net.add_hosts(dave_quantum)
    
    # Create quantum channel
    quantum_channel = QuantumChannel(
        node_1=alice_quantum, node_2=dave_quantum, length=40,
        loss_per_km=0, noise_model="simple", name="Alice-Dave Quantum Channel",
        num_bits=50
    )
    alice_quantum.add_quantum_channel(quantum_channel)
    dave_quantum.add_quantum_channel(quantum_channel)
    
    print("✅ Quantum network with student BB84 implementation created")
    
    # Step 4: Create Quantum Adapters
    print("\n🔗 Step 4: Creating quantum adapters...")
    
    # Quantum Adapter 1 (connects classical network 1 to quantum network)
    adapter1 = QuantumAdapter(
        "Adapter1", classical_net1, quantum_net, (40, 70), None,
        alice_quantum, quantum_zone, "QC_Router_QuantumAdapter-6"
    )
    
    # Quantum Adapter 2 (connects classical network 2 to quantum network)
    adapter2 = QuantumAdapter(
        "Adapter2", classical_net2, quantum_net, (120, 70), adapter1,
        dave_quantum, quantum_zone, "QC_Router_QuantumAdapter-3"
    )
    
    # Set the pairing
    adapter1.paired_adapter = adapter2
    
    # Connect adapters to classical routers
    adapter1_conn = ClassicConnection(
        router1, adapter1.local_classical_router, DEFAULT_PRESET,
        "Router1-Adapter1 Connection"
    )
    router1.add_connection(adapter1_conn)
    adapter1.local_classical_router.add_connection(adapter1_conn)
    
    adapter2_conn = ClassicConnection(
        router2, adapter2.local_classical_router, DEFAULT_PRESET,
        "Router2-Adapter2 Connection"
    )
    router2.add_connection(adapter2_conn)
    adapter2.local_classical_router.add_connection(adapter2_conn)
    
    # Add adapters to quantum network
    quantum_net.add_hosts(adapter1)
    quantum_net.add_hosts(adapter2)
    
    # Connect classical hosts to adapters
    alice_classical.add_quantum_adapter(adapter1)
    dave_classical.add_quantum_adapter(adapter2)
    
    print("✅ Quantum adapters created and connected")
    
    # Step 5: Run the Simulation
    print("\n🚀 Step 5: Running complete simulation...")
    print("📨 Sending message that will trigger QKD process...")
    
    # Send the classical message that triggers QKD
    message = "hi message"
    print(f"   {alice_classical.name} → '{message}' → {dave_classical.name}")
    
    # This should trigger the QKD process through the adapters
    alice_classical.send_data(message, dave_classical)
    
    print("\n🔄 Processing simulation events...")
    print("   Monitoring QKD initiation and BB84 protocol execution...")
    
    # Start world simulation
    world.start()
    
    # Monitor progress
    max_iterations = 150
    qkd_initiated = False
    
    for i in range(max_iterations):
        time.sleep(0.1)  # Process events
        
        # Check for QKD initiation
        if not qkd_initiated and (hasattr(adapter1, 'shared_key') and adapter1.shared_key is not None):
            qkd_initiated = True
            print("🔬 QKD process initiated!")
        
        # Show progress
        if i % 15 == 0:
            alice_measurements = len(getattr(alice_quantum, 'measurement_outcomes', []))
            dave_measurements = len(getattr(dave_quantum, 'measurement_outcomes', []))
            print(f"   Progress {i}: Alice: {alice_measurements}, Dave: {dave_measurements} measurements")
        
        # Check completion
        if qkd_status['completed']:
            print("✅ QKD completed successfully!")
            break
        
        # Check if we have shared keys in adapters
        if (hasattr(adapter1, 'shared_key') and adapter1.shared_key and 
            hasattr(adapter2, 'shared_key') and adapter2.shared_key):
            print("🔑 Shared keys detected in adapters!")
            break
    
    # Final Results
    print("\n" + "=" * 60)
    print("🏁 SIMULATION RESULTS")
    print("=" * 60)
    
    if qkd_status['completed']:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ BB84 protocol executed successfully")
        print("✅ Quantum keys shared securely")
        print("✅ Classical message transmitted through quantum-secured channel")
        alice_key = qkd_status['keys'].get('alice', [])
        print(f"🔑 Final shared key: {len(alice_key)} bits")
        
    elif hasattr(adapter1, 'shared_key') and adapter1.shared_key:
        print("🎉 ADAPTER-LEVEL SUCCESS!")
        print("✅ QKD completed at adapter level")
        print(f"🔑 Adapter 1 key: {len(adapter1.shared_key)} bits")
        print(f"🔑 Adapter 2 key: {len(adapter2.shared_key)} bits")
        
    else:
        print("❌ Simulation incomplete")
        print("💡 Troubleshooting:")
        print("   1. Check that student BB84 implementation is exported")
        print("   2. Verify all required methods are implemented")
        print("   3. Check for any error messages above")
        
        # Debug info
        alice_measurements = len(getattr(alice_quantum, 'measurement_outcomes', []))
        dave_measurements = len(getattr(dave_quantum, 'measurement_outcomes', []))
        print(f"   Final measurements: Alice {alice_measurements}, Dave {dave_measurements}")
    
    return True

# Execute the simulation
print("🎬 Starting complete quantum-classical network simulation...")
print("🎓 This uses YOUR student BB84 implementation!")
print()

try:
    success = run_complete_simulation_in_notebook()
    if success:
        print("\n✨ Simulation completed! Check the results above.")
    else:
        print("\n❌ Simulation failed to start properly.")
except Exception as e:
    print(f"\n❌ Simulation error: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Make sure all notebook cells have been run in order.")
