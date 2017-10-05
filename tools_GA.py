import time
import random
import numpy as np
from main import *

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
#def DecodeChromosome(chromosome,varRange):
    #nGenes = len(chromosome)
    #nHalf = int(nGenes/2.)      # WARNING: assumes number of genes is even
    #x1 = 0.0
    #for jx in range(nHalf):
        #x1 = x1 + chromosome[j]*2^(-j)
    #x1 = -varRange + 2*varRange*x1/(1. - 2.**(-nHalf))
    #x2 = 0.0
    #for jx in range(nHalf):
        #x2 = x2 + chromosome[j+nHalf]*2^(-j)
    #x2 = -varRange + 2*varRange*x2/(1. - 2.**(-nHalf))
# DecodeChromosome

# Evaluate variable using the fitness function
def EvaluateIndividual(wMatrix, timeSteps, iGen, nNodes, individual, nLattice, mode):
    totSum = 0.
    deltaM = sim(wMatrix, timeSteps, iGen, nNodes, individual, nLattice, mode)
    deltaMatrix = np.array(deltaM)
    #m, n = deltaMatrix.shape()
    #m = 50
    for ix in range(nLattice):
        for jx in range(nLattice):
            totSum += deltaMatrix[ix,jx]
    # DEBUG
    print('total sum on delta matrix: ' + str(totSum))
    if totSum <= int((nLattice**2)*0.1) or totSum == int(nLattice**2):
        fitness = 0.
    else:
        fitness = 1. - (1./(nLattice**2))*totSum
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
#def TournamentSelect(fitness,tournamentSelParam):
    #populationSize = len(fitness)
    #iTmp1 = 1 + int(np.random.random()*populationSize)
    #iTmp2 = 1 + int(np.random.random()*populationSize)
    #r = np.random.random()
    #if r < tournamentSelParam:
        #if fitness[iTmp1] > fitness[iTmp2]:
            #iSelected = iTmp1
        #else:
            #iSelected = iTmp2
    #else:
        #if fitness[iTmp1] > fitness[iTmp2]:
            #iSelected = iTmp2
        #else:
            #iSelected = iTmp1
    #return iSelected
# TournamentSelect

# Crossover: length preserving
#TODO implement length change
def Crossover(parent1, parent2, crossoverProb):
    r = np.random.random()
    if  r < crossoverProb:
        #someOtherNumber,nGenes = parent1.shape                # Both chromosomes must have the same length!
        crossoverPoint = np.random.randint(1,len(parent1))      # set crossover point
        # DEBUG
        #print('crossover point = ' + str(crossoverPoint))
        offspring1 = np.array(parent1)                          # copy parents
        offspring2 = np.array(parent2)

        for iz in range(len(parent1)):
            if iz < crossoverPoint:                             # exchange elements until crossoverPoint
                val1 = offspring1[iz]
                val2 = offspring2[iz]
                offspring1[iz] = val2
                offspring2[iz] = val1

        return offspring1, offspring2
    else:
        return parent1, parent2
# Crossover

# Mutation
def Mutate(parent1, parent2, mutationProb):
    r = np.random.random()
    if  r < mutationProb:
        #someOtherNumber,nGenes = chromosome1.shape
        pos1 = int(np.random.uniform(0,len(parent1)))                      # get random position to apply mutation
        pos2 = int(np.random.uniform(0,len(parent2)))
        mutation1 = np.random.normal(loc = 0.0, scale = np.sqrt(0.7))   # get mutation value from normal dist: mu = 0, sigma squared = 0.7
        mutation2 = np.random.normal(loc = 0.0, scale = np.sqrt(0.7))

        # DEBUG
        #print('Mutations: ' + str(mutation1) + ', ' + str(mutation2))
        mutatedChromosome1 = np.array(parent1)                          # create offspring from parent
        mutatedChromosome1[pos1] += mutation1                           # apply mutation

        mutatedChromosome2 = np.array(parent2)
        mutatedChromosome2[pos2] += mutation2

        return mutatedChromosome1, mutatedChromosome2
    else:
        return parent1, parent2

    #for j in range(nGenes):
        #r = np.random.random()
        #if r < mutProb:
            #mutatedChromosome[j] = 1-chromosome[j]
    #return mutatedChromosome
# Mutation

def DifferentIndex(x1, y1):
    if x1 == y1:
        return False
    else:
        return True
