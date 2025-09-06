from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import importlib.util
import sys
import tempfile
import os
from pathlib import Path

quantum_router = APIRouter(prefix="/quantum", tags=["Quantum"])

# Store for student BB84 implementations
student_implementations = {}

@quantum_router.get("/health")
async def quantum_health():
    """Health check for quantum API"""
    return {"status": "ok", "message": "Quantum API is running"}

@quantum_router.post("/update_bb84")
async def update_bb84_implementation(data: Dict[str, Any]):
    """
    Replace the hardcoded BB84 implementation with student code
    """
    try:
        implementation = data.get('implementation')
        class_name = data.get('class_name', 'BB84Protocol')
        
        if not implementation:
            raise HTTPException(status_code=400, detail="No implementation provided")
        
        # Create a temporary module to load the student's implementation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(implementation)
            temp_file_path = temp_file.name
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("student_bb84", temp_file_path)
            student_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(student_module)
            
            # Get the BB84 class
            bb84_class = getattr(student_module, class_name)
            
            # Store the implementation
            student_implementations[class_name] = bb84_class
            
            # TODO: Here we would integrate with the actual quantum host
            # For now, we'll just validate that the class can be instantiated
            test_instance = bb84_class(num_qubits=5)
            
            return {
                "status": "success", 
                "message": f"BB84 implementation '{class_name}' updated successfully",
                "class_name": class_name
            }
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating implementation: {str(e)}")

@quantum_router.post("/test_bb84")
async def test_bb84_implementation(data: Dict[str, Any]):
    """
    Test the student's BB84 implementation
    """
    try:
        num_qubits = data.get('num_qubits', 20)
        class_name = data.get('class_name', 'BB84Protocol')
        
        if class_name not in student_implementations:
            raise HTTPException(status_code=404, detail="No BB84 implementation found. Please update first.")
        
        # Get the student's implementation
        bb84_class = student_implementations[class_name]
        
        # Create instance and run protocol
        bb84 = bb84_class(num_qubits=num_qubits)
        result = bb84.run_protocol()
        
        return {
            "status": "success",
            "result": result,
            "message": "BB84 protocol executed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing BB84: {str(e)}")

@quantum_router.get("/inject_to_simulation")
async def inject_bb84_to_simulation():
    """
    Inject the student's BB84 implementation into the running simulation
    """
    try:
        if 'BB84Protocol' not in student_implementations:
            raise HTTPException(status_code=404, detail="No BB84 implementation to inject")
        
        # TODO: Here we would replace the BB84 implementation in quantum_network/host.py
        # For now, we'll just return success
        
        # Import the quantum host module
        sys.path.append(str(Path(__file__).parent.parent.parent.parent))
        from quantum_network.interactive_host import InteractiveQuantumHost as QuantumHost
        
        # Store original methods for restoration
        original_prepare_qubit = QuantumHost.prepare_qubit
        original_measure_qubit = QuantumHost.measure_qubit
        
        # Get student implementation
        student_bb84 = student_implementations['BB84Protocol']
        
        # Replace methods with student implementation
        def new_prepare_qubit(self, basis, bit):
            student_impl = student_bb84(1)  # Create temporary instance
            if basis == "Z":
                basis_int = 0
            else:  # "X"
                basis_int = 1
            return student_impl.encode_qubit(bit, basis_int)
        
        def new_measure_qubit(self, qubit, basis):
            student_impl = student_bb84(1)  # Create temporary instance
            if basis == "Z":
                basis_int = 0
            else:  # "X"
                basis_int = 1
            return student_impl.measure_qubit(qubit, basis_int)
        
        # Monkey patch the methods
        QuantumHost.prepare_qubit = new_prepare_qubit
        QuantumHost.measure_qubit = new_measure_qubit
        
        return {
            "status": "success",
            "message": "BB84 implementation injected into simulation successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error injecting to simulation: {str(e)}")


