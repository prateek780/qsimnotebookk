import time
from classical_network.connection import ClassicConnection
from classical_network.host import ClassicalHost
from classical_network.router import ClassicalRouter
from core.base_classes import World, Zone
from core.enums import NetworkType, ZoneType
from core.network import Network
from quantum_network.adapter import QuantumAdapter
from quantum_network.channel import QuantumChannel
from quantum_network.host import QuantumHost
from quantum_network.interactive_host import InteractiveQuantumHost
from quantum_network.notebook_bridge import check_simulation_readiness, NotebookIntegration
from quantum_network.repeater import QuantumRepeater
from utils.visualize import visualize_network
from classical_network.presets.connection_presets import DEFAULT_PRESET


def build_network_1(zone1):
    # Create a classical network within zone1
    classical_net = Network(
        network_type=NetworkType.CLASSICAL_NETWORK,
        location=(0, 0),
        zone=zone1,
        name="Classical Network1",
    )
    zone1.add_network(classical_net)

    # Create a classical host
    alice = ClassicalHost(
        address="192.168.1.1",
        location=(10, 10),
        network=classical_net,
        zone=zone1,
        name="Alice",
    )
    classical_net.add_hosts(alice)

    # Create another classical host
    bob = ClassicalHost(
        address="192.168.1.2",
        location=(30, 30),
        network=classical_net,
        zone=zone1,
        name="Bob",
    )
    classical_net.add_hosts(bob)

    router = ClassicalRouter(
        address="192.168.1.3",
        location=(20, 20),
        network=classical_net,
        zone=zone1,
        name="Router_Zone1",
    )
    classical_net.add_hosts(router)

    # Create a connection between Alice and Bob
    connection_ar = ClassicConnection(
        node_1=alice,
        node_2=router,
        config=DEFAULT_PRESET,
        name="Alice-Router_Zone1 Connection",
    )
    connection_rb = ClassicConnection(
        node_1=router,
        node_2=bob,
        config=DEFAULT_PRESET,
        name="Router_Zone1-Bob Connection",
    )
    alice.add_connection(connection_ar)
    router.add_connection(connection_ar)
    router.add_connection(connection_rb)
    bob.add_connection(
        connection_rb
    )  # Assuming bidirectional connection for simplicity

    return classical_net, alice, bob, router


def build_network_2(zone1):
    # Create a classical network within zone1
    classical_net = Network(
        network_type=NetworkType.CLASSICAL_NETWORK,
        location=(0, 0),
        zone=zone1,
        name="Classical Network2",
    )
    zone1.add_network(classical_net)

    # Create a classical host
    charlie = ClassicalHost(
        address="192.168.10.1",
        location=(10, 10),
        network=classical_net,
        zone=zone1,
        name="Charlie",
    )
    classical_net.add_hosts(charlie)

    # Create another classical host
    dave = ClassicalHost(
        address="192.168.10.2",
        location=(30, 30),
        network=classical_net,
        zone=zone1,
        name="Dave",
    )
    classical_net.add_hosts(dave)

    router = ClassicalRouter(
        address="192.168.10.3",
        location=(20, 20),
        network=classical_net,
        zone=zone1,
        name="Router_Zone1.1",
    )
    classical_net.add_hosts(router)

    # Create a connection between Alice and Bob
    connection_ar = ClassicConnection(
        node_1=charlie,
        node_2=router,
        config=DEFAULT_PRESET,
        name="Alice-Router_Zone1 Connection",
    )
    connection_rb = ClassicConnection(
        node_1=router,
        node_2=dave,
        config=DEFAULT_PRESET,
        name="Router_Zone1-Bob Connection",
    )
    charlie.add_connection(connection_ar)
    router.add_connection(connection_ar)
    router.add_connection(connection_rb)
    dave.add_connection(
        connection_rb
    )  # Assuming bidirectional connection for simplicity

    return classical_net, charlie, dave, router


def build_quantum_1(zone):

    # Create a quantum network
    quantum_net = Network(
        network_type=NetworkType.QUANTUM_NETWORK,
        location=(0, 0),
        zone=zone,
        name="Quantum Network",
    )
    zone.add_network(quantum_net)

    # Check if student implementation is available
    readiness = check_simulation_readiness()
    use_student_implementation = readiness.get("ready", False)
    
    if use_student_implementation:
        print("🎓 Using student BB84 implementation from notebook!")
        
        # Load student implementation
        integration = NotebookIntegration()
        alice_bridge = integration.load_student_implementation()
        dave_bridge = integration.load_student_implementation()
        
        # Create interactive quantum hosts with student implementation
        q_alice = InteractiveQuantumHost(
            address="q_alice",
            location=(10, 10),
            network=quantum_net,
            zone=zone,
            name="Qubit Alice",
            student_implementation=alice_bridge,
            send_classical_fn=lambda x: q_dave.receive_classical_data(x),
        )
        
        q_dave = InteractiveQuantumHost(
            address="q_dave",
            location=(30, 30),
            network=quantum_net,
            zone=zone,
            name="Qubit Dave",
            student_implementation=dave_bridge,
            send_classical_fn=lambda x: q_alice.receive_classical_data(x),
        )
        
    else:
        print("🔒 Using hardcoded BB84 implementation (student code not ready)")
        
        # Create standard quantum hosts
        q_alice = QuantumHost(
            address="q_alice",
            location=(10, 10),
            network=quantum_net,
            zone=zone,
            name="Qubit Alice",
            send_classical_fn=lambda x: q_dave.receive_classical_data(x),
        )
        
        q_dave = QuantumHost(
            address="q_dave",
            location=(30, 30),
            network=quantum_net,
            zone=zone,
            name="Qubit Dave",
            send_classical_fn=lambda x: q_alice.receive_classical_data(x),
        )
    
    quantum_net.add_hosts(q_alice)
    quantum_net.add_hosts(q_dave)

    channel_qb_rep = QuantumChannel(
        node_1=q_dave,
        node_2=q_alice,
        length=40,
        loss_per_km=0,
        noise_model="simple",
        name="QChannel Bob-Repeater",
    )
    q_dave.add_quantum_channel(channel_qb_rep)
    q_alice.add_quantum_channel(channel_qb_rep)

    # Add QKD completion callbacks for secure messaging
    def on_alice_qkd_complete(key):
        print(f"🔑 Alice QKD completed with {len(key)}-bit key")
        if hasattr(q_alice, 'on_qkd_completed'):
            q_alice.on_qkd_completed(key)
    
    def on_dave_qkd_complete(key):
        print(f"🔑 Dave QKD completed with {len(key)}-bit key")
        if hasattr(q_dave, 'on_qkd_completed'):
            q_dave.on_qkd_completed(key)
        
        # After both complete QKD, demonstrate secure messaging
        if hasattr(q_alice, 'shared_key') and hasattr(q_dave, 'shared_key'):
            demonstrate_quantum_secure_messaging(q_alice, q_dave)
    
    # Set QKD completion callbacks
    if hasattr(q_alice, 'qkd_completed_fn'):
        q_alice.qkd_completed_fn = on_alice_qkd_complete
    if hasattr(q_dave, 'qkd_completed_fn'):
        q_dave.qkd_completed_fn = on_dave_qkd_complete
    
    # Start QKD process if using student implementation
    if use_student_implementation:
        print("🚀 Starting BB84 protocol with student implementation...")
        q_alice.perform_qkd()
    
    return quantum_net, q_alice, q_dave

def demonstrate_quantum_secure_messaging(alice_host, bob_host):
    """Demonstrate secure messaging after QKD completion"""
    print("\n🔐 QUANTUM SECURE MESSAGING DEMONSTRATION")
    print("="*50)
    
    try:
        # Test messages
        test_messages = [
            "Hello Bob! Quantum secured message! 🔐",
            "The BB84 protocol worked perfectly! ⚛️", 
            "Secret data: Password123! 🤫"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📨 Message {i}: {message}")
            
            # Alice encrypts
            if hasattr(alice_host, 'quantum_encrypt_message'):
                encrypted = alice_host.quantum_encrypt_message(message)
                print(f"🔒 Encrypted: {encrypted.hex()}")
                
                # Bob decrypts
                if hasattr(bob_host, 'quantum_decrypt_message'):
                    decrypted = bob_host.quantum_decrypt_message(encrypted)
                    print(f"🔓 Decrypted: {decrypted}")
                    
                    if message == decrypted:
                        print("✅ Message transmitted securely!")
                    else:
                        print("❌ Decryption failed!")
        
        print("\n🎉 Quantum secure messaging demonstration complete!")
        
    except Exception as e:
        print(f"❌ Secure messaging error: {e}")


def add_hybrid(world: World):
    # Create zones
    classical_zone1 = Zone(
        size=(40, 40),
        position=(5, 50),
        zone_type=ZoneType.SECURE,
        parent_zone=world,
        name="Classical Zone 1",
    )
    network_1, alice, bob, classic_router1 = build_network_1(classical_zone1)
    world.add_zone(classical_zone1)

    classical_zone2 = Zone(
        size=(40, 40),
        position=(50, 50),
        zone_type=ZoneType.SECURE,
        parent_zone=world,
        name="Classical Zone 2",
    )
    network_2, charlie, dave, classic_router2 = build_network_2(classical_zone2)
    world.add_zone(classical_zone2)

    quantum_zone1 = Zone(
        size=(40, 40),
        position=(25, 5),
        zone_type=ZoneType.SECURE,
        parent_zone=world,
        name="Quantum Zone 2",
    )
    world.add_zone(quantum_zone1)

    quantum_network1, q_alice, q_dave = build_quantum_1(quantum_zone1)

    adapter1 = QuantumAdapter(
        "AdAdd1",
        network_1,
        quantum_network1,
        (10, 13),
        None,
        q_alice,
        quantum_zone1,
        "QAdapter1",
    )

    adapter_network1_connection = ClassicConnection(
        classic_router1,
        adapter1.local_classical_router,
        DEFAULT_PRESET,
        name="Router1 Adapter1 Connection",
    )
    adapter1.local_classical_router.add_connection(adapter_network1_connection)
    classic_router1.add_connection(adapter_network1_connection)
    quantum_network1.add_hosts(adapter1)
    alice.add_quantum_adapter(adapter1)

    adapter2 = QuantumAdapter(
        "AdAdd2",
        network_2,
        quantum_network1,
        (30, 33),
        adapter1,
        q_dave,
        quantum_zone1,
        "QAdapter2",
    )

    adapter1.add_paired_adapter(adapter2)

    adapter_network2_connection = ClassicConnection(
        classic_router2,
        adapter2.local_classical_router,
        DEFAULT_PRESET,
        name="Router2 Adapter2 Connection",
    )
    adapter2.local_classical_router.add_connection(adapter_network2_connection)
    classic_router2.add_connection(adapter_network2_connection)
    quantum_network1.add_hosts(adapter2)
    dave.add_quantum_adapter(adapter2)

    alice.send_data("HELLO WORLD", dave)


def simulate():
    # Create a world
    world = World(size=(100, 100), name="My World")
    add_hybrid(world)

    visualize_network(world, "out.png")

    world.start()


if __name__ == "__main__":
    simulate()
