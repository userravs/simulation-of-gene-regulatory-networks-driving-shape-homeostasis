#!/usr/bin/env python3
"""
Basic simulation example.

This script demonstrates how to run a simple cellular automata simulation
with a gene regulatory network.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import core.main as main
import core.tools as tools

def run_basic_simulation():
    """Run a basic simulation with default parameters."""
    
    # Default parameters
    nNodes = 25
    timeSteps = 50
    nLattice = 20
    mode = False  # Visualization mode
    
    # Create a simple weight matrix (random)
    import numpy as np
    wMatrix = np.random.rand(nNodes, nNodes) * 2 - 1  # Random weights between -1 and 1
    
    print(f"Running simulation with:")
    print(f"  Nodes: {nNodes}")
    print(f"  Time steps: {timeSteps}")
    print(f"  Lattice size: {nLattice}x{nLattice}")
    print(f"  Mode: {'Visualization' if mode else 'Fitness'}")
    
    # Run simulation
    main.sim(wMatrix, timeSteps, nNodes, nLattice, mode)
    
    print("Simulation completed!")

if __name__ == "__main__":
    run_basic_simulation()
