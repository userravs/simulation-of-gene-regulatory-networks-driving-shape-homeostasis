#!/usr/bin/env python3
"""
Genetic algorithm example.

This script demonstrates how to run the genetic algorithm to evolve
gene regulatory networks.
"""

import sys
import os
import numpy as np

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import evolution.main_GA as main_GA
import evolution.tools_GA as tools_GA

def run_evolution_example():
    """Run a simple genetic algorithm example."""
    
    # Small-scale parameters for demonstration
    nProcs = 2
    popSize = 4
    nNodes = 10
    nGenes = nNodes**2
    nOfGenerations = 5
    timeSteps = 50
    nLattice = 15
    mode = True  # Fitness mode (no visualization)
    
    print(f"Running genetic algorithm with:")
    print(f"  Population size: {popSize}")
    print(f"  Nodes: {nNodes}")
    print(f"  Generations: {nOfGenerations}")
    print(f"  Lattice size: {nLattice}x{nLattice}")
    print(f"  Processes: {nProcs}")
    
    # Create a simple population
    population = np.random.rand(popSize, nGenes) * 2 - 1
    
    # Run a few generations
    for gen in range(nOfGenerations):
        print(f"\nGeneration {gen + 1}/{nOfGenerations}")
        
        # Evaluate fitness (simplified)
        fitness = np.zeros(popSize)
        for i in range(popSize):
            wMatrix = population[i].reshape(nNodes, nNodes)
            # Run simulation and calculate fitness
            fitness[i] = np.random.random()  # Placeholder fitness
        
        print(f"  Best fitness: {np.max(fitness):.3f}")
        print(f"  Average fitness: {np.mean(fitness):.3f}")
    
    print("\nEvolution completed!")

if __name__ == "__main__":
    run_evolution_example()
