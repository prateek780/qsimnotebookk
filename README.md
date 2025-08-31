# Quantum Network Simulator 🌐⚛️

A hybrid classical-quantum network simulator for interactive learning and research.

## 🚀 Try it Online - No Installation Required!

Launch the interactive quantum networking notebooks directly in your browser:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/prateek780/qsimnotebookk/main?filepath=quantum_networking_interactive.ipynb)

### Available Interactive Notebooks:
- 📚 **[Introduction to Quantum Networking](https://mybinder.org/v2/gh/prateek780/qsimnotebookk/main?filepath=quantum_networking_interactive.ipynb)** - Start here for fundamentals
- 🔐 **[BB84 Quantum Key Distribution](https://mybinder.org/v2/gh/prateek780/qsimnotebookk/main?filepath=quantum_networking_bb84.ipynb)** - Hands-on cryptography
- 🎮 **[General Quantum Networking](https://mybinder.org/v2/gh/prateek780/qsimnotebookk/main?filepath=qnetorking.ipynb)** - Advanced concepts


*Click any badge above to launch the notebook in a live, interactive environment!*

## Project Structure

```
simulator_1/
├── classical_network/ # Classical network simulation components
├── core/              # Core simulation engine
├── quantum_network/   # Quantum network simulation components
├── server/            # API server implementation
├── ui/                # User interface
├── utils/             # Utility functions and helpers
├── json_parser.py     # Start simulator by parsing json file
├── main.py            # Main entry point for Python CLI based simulator (No UI)
├── requirements.txt   # Python dependencies
└── start.py           # Startup script (API Server)
```

## Overview

This simulator provides a dual-purpose environment for testing both classical and quantum network interactions. It can be used for research, development, and educational purposes.

## 🎓 For Students: Using This Simulator in Your Own Notebooks

You can import and use this quantum networking simulator in your own Jupyter notebooks! Here are several ways:

### Method 1: Direct Import from GitHub (Recommended for Binder)
```python
# In your notebook cell:
import sys
import subprocess

# Clone the simulator (one-time setup)
!git clone https://github.com/prateek780/qsimnotebookk.git quantum_sim

# Add to Python path
sys.path.append('./quantum_sim')

# Import the quantum networking modules
from quantum_network.host import QuantumHost
from quantum_network.channel import QuantumChannel
# ... other imports
```

### Method 2: Install as a Package
```python
# Install directly from GitHub
!pip install git+https://github.com/prateek780/qsimnotebookk.git

# Then import normally
from quantum_network import QuantumHost, QuantumChannel
```

### Method 3: Copy Essential Files
Copy these key files to your project:
- `quantum_network/` directory (core simulator)
- `utils/quantum_encryption.py` (utilities)
- `binder_requirements.txt` (dependencies)

### Example Usage in Student Notebooks:
```python
# Create quantum hosts
alice = QuantumHost("Alice")
bob = QuantumHost("Bob")

# Set up quantum channel
channel = QuantumChannel(alice, bob, error_rate=0.1)

# Run BB84 protocol
alice.bb84_send_qubits(bob, key_length=100)
shared_key = bob.bb84_receive_qubits()

print(f"Shared quantum key: {shared_key}")
```

## 💻 Local Installation (Advanced Users)

1. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r binder_requirements.txt  # Minimal deps
   # OR
   pip install -r requirements.txt         # Full deps
   ```

3. Install node packages for UI (optional):
   ```
   cd ui
   npm install
   ```

## GUI Usage

Start the API Server:
```
python start.py
```

Start UI:
```
cd ui
npm run dev
```

## CLI Usage

Or run the main application directly:
```
python main.py
```

## Configuration

Network topology and parameters can be configured in the `network.json` file.

## Components

- **Classical Network**: Traditional network simulation
- **Quantum Network**: Quantum communication protocols and algorithms
- **Core**: Central simulation engine that coordinates between classical and quantum components
- **Server**: Backend server for remote access and control
- **UI**: User interface for visualization and interaction

## Output

The simulator produces various outputs:
- Text logs in `logs/` directory and `log.txt`
- Visualization images (`out.png`, `out_parsed.png`)
- Textual results (`out.txt`)

## 🌐 Binder Deployment Guide

This repository is configured to work seamlessly with [MyBinder.org](https://mybinder.org) for zero-installation access.

### For Repository Owners:
1. Push your code to GitHub
2. Update the Binder links in this README with your actual `USERNAME/REPO_NAME`
3. The Binder configuration files are already included:
   - `binder_requirements.txt` - Minimal dependencies for fast builds
   - `runtime.txt` - Python version specification
   - `postBuild` - Setup script for Jupyter extensions
   - `.binder/environment.yml` - Conda environment (alternative)

### Binder Link Format:
```
https://mybinder.org/v2/gh/USERNAME/REPO_NAME/BRANCH?filepath=NOTEBOOK.ipynb
```

### Build Time Optimization:
- Uses minimal dependencies in `binder_requirements.txt`
- Specifies Python 3.10 for faster builds
- Pre-configures Jupyter widgets and extensions

### Troubleshooting Binder:
- Build fails? Check `binder_requirements.txt` for conflicting versions
- Slow builds? Consider removing optional dependencies like `qiskit`
- Import errors? Ensure all required files are in the repository

## 🤝 Contributing

Students and educators are welcome to contribute:
- Add new quantum protocols
- Improve notebook explanations
- Fix bugs or optimize performance
- Submit educational examples

## 📄 License

This educational simulator is open source. Please check the LICENSE file for details.
