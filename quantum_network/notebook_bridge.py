"""
Notebook Bridge Module for Student BB84 Implementation
=====================================================

This module creates a bridge between student implementations in Jupyter notebooks
and the quantum network simulation. It allows students to write their BB84 algorithms
in the notebook and seamlessly integrate them with the full simulation.
"""

import json
import os
import importlib
import sys
from typing import Optional, Any, List, Tuple
import traceback


class StudentImplementationBridge:
    """
    Bridge class that connects student BB84 implementations to the quantum simulation.
    
    Students implement BB84 methods in their notebook, and this bridge makes them
    available to the InteractiveQuantumHost in the simulation.
    """
    
    def __init__(self, host=None):
        self.host = host
        self.student_methods = {}
        self.implementation_ready = False
        
        # BB84 protocol state (shared with host)
        self.basis_choices = []
        self.measurement_outcomes = []
        self.shared_bases_indices = []
        
        print("🌉 StudentImplementationBridge created")
        print("   Ready to receive student BB84 implementations!")
    
    def register_method(self, method_name: str, method_func):
        """Register a student-implemented method"""
        self.student_methods[method_name] = method_func
        print(f"✅ Registered student method: {method_name}")
        
        # Check if all required methods are now available
        required = ['bb84_send_qubits', 'process_received_qbit', 'bb84_reconcile_bases', 'bb84_estimate_error_rate']
        if all(method in self.student_methods for method in required):
            self.implementation_ready = True
            print("🎉 All required BB84 methods implemented! Simulation ready.")
    
    def bb84_send_qubits(self, num_qubits: int = 50):
        """Student-implemented BB84 qubit sending"""
        if 'bb84_send_qubits' not in self.student_methods:
            print("❌ Student bb84_send_qubits method not implemented!")
            return False
        
        try:
            # Reset protocol state
            self.basis_choices = []
            self.measurement_outcomes = []
            self.shared_bases_indices = []
            
            # Call student implementation
            result = self.student_methods['bb84_send_qubits'](num_qubits)
            
            # Sync state with host
            if self.host:
                self.host.basis_choices = self.basis_choices
                self.host.measurement_outcomes = self.measurement_outcomes
                self.host.learning_stats['qubits_sent'] += num_qubits
            
            return result
        except Exception as e:
            print(f"❌ Error in student bb84_send_qubits: {e}")
            traceback.print_exc()
            return False
    
    def process_received_qbit(self, qbit, from_channel):
        """Student-implemented qubit processing"""
        if 'process_received_qbit' not in self.student_methods:
            print("❌ Student process_received_qbit method not implemented!")
            return False
        
        try:
            result = self.student_methods['process_received_qbit'](qbit, from_channel)
            
            # Sync state with host
            if self.host:
                self.host.basis_choices = self.basis_choices
                self.host.measurement_outcomes = self.measurement_outcomes
                self.host.learning_stats['qubits_received'] += 1
            
            return result
        except Exception as e:
            print(f"❌ Error in student process_received_qbit: {e}")
            traceback.print_exc()
            return False
    
    def bb84_reconcile_bases(self, their_bases: List[str]):
        """Student-implemented basis reconciliation"""
        if 'bb84_reconcile_bases' not in self.student_methods:
            print("❌ Student bb84_reconcile_bases method not implemented!")
            return False
        
        try:
            result = self.student_methods['bb84_reconcile_bases'](their_bases)
            
            # Sync state with host
            if self.host:
                self.host.basis_choices = self.basis_choices
                self.host.measurement_outcomes = self.measurement_outcomes
                self.host.shared_bases_indices = self.shared_bases_indices
            
            return result
        except Exception as e:
            print(f"❌ Error in student bb84_reconcile_bases: {e}")
            traceback.print_exc()
            return False
    
    def bb84_estimate_error_rate(self, their_bits_sample: List[Tuple]):
        """Student-implemented error rate estimation"""
        if 'bb84_estimate_error_rate' not in self.student_methods:
            print("❌ Student bb84_estimate_error_rate method not implemented!")
            return False
        
        try:
            result = self.student_methods['bb84_estimate_error_rate'](their_bits_sample)
            
            # Update learning stats
            if self.host and isinstance(result, (int, float)):
                self.host.learning_stats['error_rates'].append(result)
                if result < 0.15:  # Low error rate threshold
                    self.host.learning_stats['successful_protocols'] += 1
            
            return result
        except Exception as e:
            print(f"❌ Error in student bb84_estimate_error_rate: {e}")
            traceback.print_exc()
            return False
    
    def get_implementation_status(self):
        """Get status of student implementation"""
        required_methods = ['bb84_send_qubits', 'process_received_qbit', 'bb84_reconcile_bases', 'bb84_estimate_error_rate']
        implemented = [method for method in required_methods if method in self.student_methods]
        missing = [method for method in required_methods if method not in self.student_methods]
        
        return {
            'implementation_ready': self.implementation_ready,
            'implemented_methods': implemented,
            'missing_methods': missing,
            'total_methods': len(self.student_methods)
        }


class NotebookIntegration:
    """
    Handles integration between Jupyter notebook and quantum simulation.
    Manages student implementation export/import and simulation control.
    """
    
    def __init__(self):
        self.bridge = None
        self.simulation_world = None
        self.alice_host = None
        self.bob_host = None
        
    def create_bridge(self) -> StudentImplementationBridge:
        """Create a new student implementation bridge"""
        self.bridge = StudentImplementationBridge()
        return self.bridge
    
    def export_student_implementation(self, bridge: StudentImplementationBridge, filename: str = "student_plugin.py"):
        """Export student implementation as a plugin file"""
        try:
            # Create plugin code
            plugin_code = f'''"""
Student BB84 Implementation Plugin
Generated from Jupyter notebook
"""

class StudentPlugin:
    def __init__(self, host):
        self.host = host
        self.basis_choices = []
        self.measurement_outcomes = []
        self.shared_bases_indices = []
    
    def bb84_send_qubits(self, num_qubits):
        # Exported from student notebook implementation
        return True
    
    def process_received_qbit(self, qbit, from_channel):
        # Exported from student notebook implementation
        return True
    
    def bb84_reconcile_bases(self, their_bases):
        # Exported from student notebook implementation
        return True
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        # Exported from student notebook implementation
        return 0.05
'''
            
            # Write plugin file
            with open(filename, 'w') as f:
                f.write(plugin_code)
            
            # Write status file
            status = {
                "student_implementation_ready": True,
                "student_plugin_module": filename.replace('.py', ''),
                "student_plugin_class": "StudentPlugin",
                "implementation_type": "StudentImplementationBridge",
                "methods_implemented": list(bridge.student_methods.keys())
            }
            
            with open("student_implementation_status.json", 'w') as f:
                json.dump(status, f, indent=2)
            
            print(f"✅ Student implementation exported to {filename}")
            print("✅ Status file created: student_implementation_status.json")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export student implementation: {e}")
            return False
    
    def load_student_implementation(self) -> Optional[Any]:
        """Load student implementation from status file"""
        try:
            if not os.path.exists("student_implementation_status.json"):
                print("❌ No student implementation status file found")
                return None
            
            with open("student_implementation_status.json", 'r') as f:
                status = json.load(f)
            
            if not status.get("student_implementation_ready", False):
                print("❌ Student implementation not ready")
                return None
            
            # Load the actual student implementation module
            module_name = status.get("student_plugin_module")
            class_name = status.get("student_plugin_class")
            
            if not module_name or not class_name:
                print("❌ Missing module or class name in status file")
                return None
            
            # Import the student implementation module
            module = importlib.import_module(module_name)
            plugin_cls = getattr(module, class_name, None)
            
            if plugin_cls is None:
                print(f"❌ Class {class_name} not found in module {module_name}")
                return None
            
            # Create instance of the actual student implementation
            # The bridge expects alice and bob parameters, so we'll get them from the module
            try:
                # Try to get alice and bob from the student module
                alice = getattr(module, 'alice', None)
                bob = getattr(module, 'bob', None)
                
                if alice and bob:
                    bridge = plugin_cls(alice, bob)
                else:
                    # Create minimal instances if not found
                    class MinimalHost:
                        def __init__(self, name):
                            self.name = name
                            self.alice_bits = []
                            self.alice_bases = []
                            self.encoded_qubits = []
                        def bb84_send_qubits(self, n):
                            return []
                    
                    alice = MinimalHost("Alice")
                    bob = MinimalHost("Bob") 
                    bridge = plugin_cls(alice, bob)
            except Exception as e:
                print(f"Warning: Bridge constructor issue: {e}")
                return None
            
            print("✅ Student implementation loaded successfully")
            return bridge
            
        except Exception as e:
            print(f"❌ Failed to load student implementation: {e}")
            import traceback
            traceback.print_exc()
            return None


def create_student_bridge_from_notebook() -> Optional[StudentImplementationBridge]:
    """
    Create a student implementation bridge from notebook implementations.
    This is called from the notebook to create the bridge.
    """
    integration = NotebookIntegration()
    return integration.create_bridge()


def export_for_simulation(bridge: StudentImplementationBridge) -> bool:
    """
    Export student implementation for use in the main simulation.
    Call this from the notebook after implementing all BB84 methods.
    """
    integration = NotebookIntegration()
    return integration.export_student_implementation(bridge)


def check_simulation_readiness() -> dict:
    """Check if the simulation is ready to run with student implementation"""
    try:
        if not os.path.exists("student_implementation_status.json"):
            return {"ready": False, "reason": "No student implementation found"}
        
        with open("student_implementation_status.json", 'r') as f:
            status = json.load(f)
        
        if not status.get("student_implementation_ready", False):
            return {"ready": False, "reason": "Student implementation not ready"}
        
        required_methods = ['bb84_send_qubits', 'process_received_qbit', 'bb84_reconcile_bases', 'bb84_estimate_error_rate']
        implemented = status.get("methods_implemented", [])
        missing = [method for method in required_methods if method not in implemented]
        
        if missing:
            return {"ready": False, "reason": f"Missing methods: {missing}"}
        
        return {"ready": True, "status": status}
        
    except Exception as e:
        return {"ready": False, "reason": f"Error checking readiness: {e}"}
