# Auto-generated bridge for simulation
import sys
import os
sys.path.append(os.path.dirname(__file__))

from student_bridge_implementation import StudentImplementationBridge as BaseBridge, alice, bob

class StudentImplementationBridge:
    """Bridge wrapper that matches simulation expectations"""
    def __init__(self, host):
        self.host = host
        # Create the actual bridge with alice and bob
        self._bridge = BaseBridge(alice, bob)
        self._bridge.host = host
    
    def bb84_send_qubits(self, num_qubits):
        return self._bridge.bb84_send_qubits(num_qubits)
    
    def process_received_qbit(self, qbit, from_channel):
        return self._bridge.process_received_qbit(qbit, from_channel)
    
    def bb84_reconcile_bases(self, their_bases):
        return self._bridge.bb84_reconcile_bases(their_bases)
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        return self._bridge.bb84_estimate_error_rate(their_bits_sample)
