#!/usr/bin/env python3
"""
Setup script for Quantum Network Simulator
Enables installation as a Python package for easy import in student notebooks
"""

from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from binder_requirements.txt
with open("binder_requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="quantum-network-simulator",
    version="1.0.0",
    author="Quantum Networking Team",
    description="Interactive quantum networking simulator for education and research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prateek780/qsimnotebookk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "full": [
            "qiskit>=1.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
    },
    entry_points={
        "console_scripts": [
            "quantum-sim=main:main",
        ],
    },
)
