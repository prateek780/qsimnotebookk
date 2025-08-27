"""
Educational Quantum Host Module
==============================

This module now uses the InteractiveQuantumHost for educational purposes.
Students can implement their own quantum networking protocols by creating
custom implementations and passing them to the InteractiveQuantumHost.

The original hardcoded implementation has been preserved in host_original.py
"""

# Import the interactive educational version
from quantum_network.interactive_host import InteractiveQuantumHost

# For backward compatibility, alias the class
QuantumHost = InteractiveQuantumHost

print("🎓 Educational Quantum Host Module Loaded!")
print("💡 Students can now implement custom quantum protocols!")
print("📖 See quantum_networking_interactive.ipynb for examples")