import time
import random 
import numpy as np

# this doesn't have to be a function, its just one line...
#def InitializePopulation(populationSize, numberOfGenes):
    #population = np.random.randint(0,2,size=(populationSize, numberOfGenes))
    ##population = np.zeros([populationSize, numberOfGenes]);
    ##for ix in range(populationSize):
        ##for jx in range(numberOfGenes):
            ##s = np.random.random()
            ##if s < 0.5:
                ##population[ix,jx] = 0
            ##else:
                ##population[ix,jx] = 1
    #return population
# InitializePopulation

# translate the chromosome into actual variables 
def DecodeChromosome(chromosome,varRange):
    nGenes = len(chromosome)
    nHalf = int(nGenes/2.)      # WARNING: assumes number of genes is even
    x1 = 0.0
    for jx in range(nHalf):
        x1 = x1 + chromosome[j]*2^(-j)
    x1 = -varRange + 2*varRange*x1/(1. - 2.**(-nHalf))
    x2 = 0.0
    for jx in range(nHalf):
        x2 = x2 + chromosome[j+nHalf]*2^(-j)
    x2 = -varRange + 2*varRange*x2/(1. - 2.**(-nHalf))
# DecodeChromosome

# Evaluate variable using the fitness function
def EvaluateIndividual(x):
    totSum = 0
    for ix in range(border):
        for jx in range(border):
            totSum += DiracDelta(ix,jx)
    fitness = 1. - (1./(lSize**2))*totSum
    return fitness
# EvaluateIndividual

# Dirac's delta function
def DiracDelta(a, b):
    if a == b:
        return 0
    else: 
        return 1
# DiracDelta

# Tournament selection, tournament size 2
def TournamentSelect(fitness,tournamentSelParam)
    populationSize = len(fitness)
    iTmp1 = 1 + int(np.random.random()*populationSize)
    iTmp2 = 1 + int(np.random.random()*populationSize)
    r = np.random.random()
    if r < tournamentSelParam:
        if fitness[iTmp1] > fitness[iTmp2]:
            iSelected = iTmp1
        else:
            iSelected = iTmp2
    else:
        if fitness[iTmp1] > fitness[iTmp2]:
            iSelected = iTmp2
        else:
            iSelected = iTmp1
    return iSelected
# TournamentSelect

# Crossover
def Cross(chromosome1,chromosome2):
    someOtherNumber,nGenes = chromosome1.shape                # Both chromosomes must have the same length!
    crossoverPoint = 1 + int(np.random.random()*(nGenes-1))
    newChromosomePair = np.zeros([2,nGenes])
    for j in range(nGenes):
        if j < crossoverPoint:
            newChromosomePair[0,j] = chromosome1[j]
            newChromosomePair[1,j] = chromosome2[j]
        else:
            newChromosomePair[0,j] = chromosome2[j]
            newChromosomePair[1,j] = chromosome1[j]
    return newChromosomePair
# Cross

# Mutation
def Mutate(chromosome,mutProb):
    someOtherNumber,nGenes = chromosome1.shape
    mutatedChromosome = np.array(chromosome)
    for j in range(nGenes):
        r = np.random.random()
        if r < mutProb:
            mutatedChromosome[j] = 1-chromosome[j]
    return mutatedChromosome
# Mutate
