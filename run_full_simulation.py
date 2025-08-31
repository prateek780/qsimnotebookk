#!/usr/bin/env python3
"""
Complete Simulation Runner - UI + Backend + Student BB84
======================================================

This script starts both the backend and frontend servers and ensures
your student BB84 implementation is properly integrated with the UI.
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def check_student_implementation():
    """Check if student implementation is ready"""
    if not os.path.exists("student_implementation_status.json"):
        print("❌ Student implementation not found!")
        print("💡 Run the Export cell in your notebook first!")
        return False
    
    try:
        with open("student_implementation_status.json", 'r') as f:
            status = json.load(f)
        
        if status.get("student_implementation_ready", False):
            print("✅ Student BB84 implementation detected!")
            return True
        else:
            print("❌ Student implementation not ready")
            return False
    except Exception as e:
        print(f"❌ Error checking student implementation: {e}")
        return False

def start_backend_server():
    """Start the backend server"""
    print("🚀 Starting backend server on port 5174...")
    
    try:
        # Set environment variables to avoid Redis issues
        env = os.environ.copy()
        env.update({
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_USERNAME": "",
            "REDIS_PASSWORD": "",
            "REDIS_DB": "0",
            "REDIS_SSL": "False"
        })
        
        backend_process = subprocess.Popen(
            [sys.executable, "start.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give backend time to start
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend server started successfully!")
            return backend_process
        else:
            print("❌ Backend server failed to start")
            stdout, stderr = backend_process.communicate()
            print(f"Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend_server():
    """Start the frontend server"""
    print("🚀 Starting frontend server on port 5173...")
    
    try:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="ui",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give frontend time to start
        time.sleep(5)
        
        if frontend_process.poll() is None:
            print("✅ Frontend server started successfully!")
            return frontend_process
        else:
            print("❌ Frontend server failed to start")
            stdout, stderr = frontend_process.communicate()
            print(f"Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def run_simulation_with_ui():
    """Run the complete simulation with UI integration"""
    print("🌐 COMPLETE QUANTUM SIMULATION WITH UI INTEGRATION")
    print("="*60)
    print("🎓 Using YOUR student BB84 implementation")
    print("🔗 Backend (5174) + Frontend (5173) + Student Code")
    print("="*60)
    
    # Check student implementation
    if not check_student_implementation():
        return False
    
    # Start backend
    backend = start_backend_server()
    if not backend:
        print("❌ Cannot start without backend server")
        return False
    
    # Start frontend
    frontend = start_frontend_server()
    if not frontend:
        print("❌ Cannot start without frontend server")
        backend.terminate()
        return False
    
    try:
        print("\n🌟 SIMULATION SERVERS RUNNING!")
        print("="*40)
        print("🔧 Backend API: http://localhost:5174")
        print("🌐 Frontend UI: http://localhost:5173")
        print("🎓 Student BB84: INTEGRATED")
        print("="*40)
        print()
        print("🎯 What to do now:")
        print("1. Open http://localhost:5173 in your browser")
        print("2. Create quantum hosts in the UI")
        print("3. Start the simulation")
        print("4. Watch YOUR BB84 algorithms run in real-time!")
        print("5. See the complete process: QKD → Key Sharing → Encryption")
        print()
        print("💡 Your student implementation will be automatically detected")
        print("💡 No more 'VIBE CODE' blocking messages!")
        print("💡 The UI will show your BB84 in action!")
        print()
        print("Press Ctrl+C to stop both servers...")
        
        # Keep servers running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend.poll() is not None:
                print("❌ Backend server stopped")
                break
            if frontend.poll() is not None:
                print("❌ Frontend server stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        
    finally:
        # Clean shutdown
        if backend and backend.poll() is None:
            backend.terminate()
            print("✅ Backend server stopped")
        
        if frontend and frontend.poll() is None:
            frontend.terminate()
            print("✅ Frontend server stopped")
    
    return True

if __name__ == "__main__":
    print("🎓 Complete Quantum Simulation with UI")
    print("   Student BB84 + Backend + Frontend Integration")
    print()
    
    success = run_simulation_with_ui()
    
    if success:
        print("✅ Simulation completed successfully!")
    else:
        print("❌ Simulation setup failed")
        print("💡 Try running servers manually:")
        print("   Terminal 1: python start.py")
        print("   Terminal 2: cd ui && npm run dev")
