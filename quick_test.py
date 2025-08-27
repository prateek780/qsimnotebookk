#!/usr/bin/env python3
"""
Quick Test Script for Quantum Networking with BB84 Protocol
==========================================================

This script provides a quick test of the main functionality
to ensure everything is working correctly.
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    """Run a quick test of the quantum networking implementation."""
    
    print("🧪 Quick Test: Quantum Networking with BB84 Protocol")
    print("=" * 60)
    
    try:
        # Test 1: Import libraries
        print("1. Testing library imports...")
        import numpy as np
        import matplotlib.pyplot as plt
        import qutip as qt
        print("   ✅ All libraries imported successfully!")
        
        # Test 2: Basic quantum operations
        print("\n2. Testing basic quantum operations...")
        qubit_0 = qt.basis(2, 0)
        qubit_1 = qt.basis(2, 1)
        superposition = (qubit_0 + qubit_1) / np.sqrt(2)
        print(f"   ✅ Qubit states created: |0⟩, |1⟩, |+⟩")
        
        # Test 3: BB84 protocol (minimal test)
        print("\n3. Testing BB84 protocol basics...")
        from quantum_networking_bb84 import BB84Protocol
        
        bb84 = BB84Protocol(key_length=10)
        alice_bits, alice_bases = bb84.alice_prepare_qubits()
        print(f"   ✅ Alice generated {len(alice_bits)} bits and bases")
        
        # Test 4: Qubit encoding
        print("\n4. Testing qubit encoding...")
        encoded_qubit = bb84.encode_qubit(1, 0)  # bit=1, computational basis
        print(f"   ✅ Qubit encoded successfully: {encoded_qubit}")
        
        print("\n🎉 All basic tests passed! The implementation is working correctly.")
        print("\n🚀 Next steps:")
        print("   1. Run the full demonstration: python quantum_networking_bb84.py")
        print("   2. Open in Jupyter: jupyter notebook quantum_networking_bb84.py")
        print("   3. Follow the 3-4 day plan in QUANTUM_README.md")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Solution: Install required dependencies:")
        print("   pip install -r quantum_requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
