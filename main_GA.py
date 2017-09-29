import time
import random 
import numpy as np

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       PARAMETERS                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
popSize = 30                                                # Population size
nGenes = 40                                                 # Number of genes
crossoverProb = 0.8                                         # Crossover probability
mutationProb = 0.025                                        # Mutation probability
tournamentSelParam = 0.75                                   # Tournament selection parameter
varRange = 3.0                                              # variable range
nOfGenerations = 100
fitness = np.zeros([popSize])                               # fitness array

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       INITIALISATION             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
population = InitializePopulation(popSize, numberOfGenes)   # call initialization function, a random set of chromosomes is generated

for iGen in range(nOfGenerations):
    maximumFitness = 0.0 # Assumes non-negative fitness values!
    xBest = np.zeros([1,2]) # [0 0]
    bestIndividualIndex = 0

    # chromosomes get decoded and evaluated
    for ix in range(0,popSize,2):                               # only every other individual gets considered
        chromosome = population[i,:]
        x = DecodeChromosome(chromosome, variableRange)
        fitness[i] = EvaluateIndividual(x)
        if fitness[i] > maximumFitness:
            maximumFitness = fitness[i]
            bestIndividualIndex = i
            xBest = x
    tempPopulation = np.array(population)

    for i in range(popSize):
        i1 = TournamentSelect(fitness,tournamentSelParam)
        i2 = TournamentSelect(fitness,tournamentSelParam)
        chromosome1 = population[i1,:]
        chromosome2 = population[i2,:]
        tempPopulation[i,:] = chromosome1
        tempPopulation[i+1,:] = chromosome2

        r = np.random.random()
        if r < crossProb:
            newChromosomePair = Cross(chromosome1,chromosome2)
            tempPopulation[i,:] = newChromosomePair[1,:]
            tempPopulation[i+1,:] = newChromosomePair[2,:]
        else:
            tempPopulation[i,:] = chromosome1
            tempPopulation[i+1,:] = chromosome2
    # Loop over population

    for i in range(popSize):
        originalChromosome = tempPopulation[i,:]
        mutatedChromosome = Mutate(originalChromosome,mutProb)
        tempPopulation[i,:] = mutatedChromosome

    tempPopulation[1,:] = population[bestIndividualIndex,:]
    population = np.array(tempPopulation)
