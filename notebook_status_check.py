#!/usr/bin/env python3
"""
Notebook Status Check - Debug Helper
===================================

This script helps debug issues with the notebook integration.
Run this to check if everything is properly set up.
"""

import os
import json
import sys
import importlib.util

def check_notebook_integration():
    """Check if notebook integration is working properly"""
    print("🔍 NOTEBOOK INTEGRATION STATUS CHECK")
    print("="*50)
    
    issues = []
    
    # 1. Check student implementation status file
    print("1. Checking student implementation status...")
    if os.path.exists("student_implementation_status.json"):
        try:
            with open("student_implementation_status.json", 'r') as f:
                status = json.load(f)
            
            if status.get("student_implementation_ready", False):
                print("   ✅ Student implementation status: READY")
                print(f"   📋 Module: {status.get('student_plugin_module', 'N/A')}")
                print(f"   📋 Class: {status.get('student_plugin_class', 'N/A')}")
                print(f"   📋 Methods: {status.get('methods_implemented', [])}")
            else:
                print("   ❌ Student implementation status: NOT READY")
                issues.append("Student implementation not marked as ready")
        except Exception as e:
            print(f"   ❌ Error reading status file: {e}")
            issues.append(f"Status file error: {e}")
    else:
        print("   ❌ Student implementation status file not found")
        issues.append("Missing student_implementation_status.json")
    
    # 2. Check student bridge file
    print("\n2. Checking student bridge file...")
    if os.path.exists("student_impl_bridge.py"):
        try:
            spec = importlib.util.spec_from_file_location("student_impl_bridge", "student_impl_bridge.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'StudentImplementationBridge'):
                print("   ✅ StudentImplementationBridge class found")
                
                # Check if simulation_bridge exists
                if hasattr(module, 'simulation_bridge'):
                    print("   ✅ simulation_bridge instance found")
                else:
                    print("   ❌ simulation_bridge instance not found")
                    issues.append("Missing simulation_bridge instance")
                    
            else:
                print("   ❌ StudentImplementationBridge class not found")
                issues.append("Missing StudentImplementationBridge class")
                
        except Exception as e:
            print(f"   ❌ Error importing bridge file: {e}")
            issues.append(f"Bridge import error: {e}")
    else:
        print("   ❌ student_impl_bridge.py not found")
        issues.append("Missing student_impl_bridge.py")
    
    # 3. Check required dependencies
    print("\n3. Checking dependencies...")
    deps = ['numpy', 'qutip', 'pydantic']
    for dep in deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}: INSTALLED")
        except ImportError:
            print(f"   ❌ {dep}: NOT INSTALLED")
            issues.append(f"Missing dependency: {dep}")
    
    # 4. Check main simulation files
    print("\n4. Checking simulation files...")
    files = ['main.py', 'start.py', 'quantum_network/interactive_host.py']
    for file in files:
        if os.path.exists(file):
            print(f"   ✅ {file}: EXISTS")
        else:
            print(f"   ❌ {file}: MISSING")
            issues.append(f"Missing file: {file}")
    
    # 5. Summary
    print("\n" + "="*50)
    if not issues:
        print("🎉 ALL CHECKS PASSED!")
        print("Your notebook integration is ready to run!")
        print("\n🚀 Next steps:")
        print("1. Run Cell 29 (Direct Simulation) to test")
        print("2. Run Cell 28 (Full UI) for complete experience")
    else:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        
        print("\n💡 SOLUTIONS:")
        if "Missing student_implementation_status.json" in str(issues):
            print("• Run the Export Implementation cell in the notebook")
        if "Missing dependency" in str(issues):
            print("• Install missing dependencies: pip install numpy qutip pydantic")
        if "Bridge import error" in str(issues):
            print("• Check your StudentQuantumHost implementation in the notebook")
        
    return len(issues) == 0

if __name__ == "__main__":
    check_notebook_integration()
