import time
import random 
import numpy as np

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       PARAMETERS                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
popSize = 30                                                # Population size
nNodes = 25
nGenes = nNodes**2                                                 # Number of genes
crossoverProb = 0.8                                         # Crossover probability
mutationProb = 0.025                                        # Mutation probability
tournamentSelParam = 0.75                                   # Tournament selection parameter
eliteNum = 6                                              # number of elite solutions to carry to next generation
nOfGenerations = 200
fitness = np.zeros([popSize,2])                               # fitness array
posList = []
eliteIndividuals = []
dtype = [('fitness',float),('position',int)]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       INITIALISATION             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#population = InitializePopulation(popSize, numberOfGenes)  # call initialization function, a random set of chromosomes is generated
population = np.random.random(size=(popSize, nGenes))


for iGen in range(nOfGenerations):
    maxFitness = 0. # Assumes non-negative fitness values!
    fitness = np.array(('',-1),dtype = dtype)
    #wBest = np.zeros(nGenes) # [0 0]
    bestIndividualIndex = 0

    # chromosomes get decoded and evaluated
    for ix in range(popSize):
        posList[ix] = ix
        chromosome = np.array(population[ix,:])                 # loop through all chromosomes
        wMatrix = -1 + 2*chromosome.reshape(nNodes,nNodes)      # decode chromosome,i.e., transform into matrix
        np.append(fitness, EvaluateIndividual(wMatrix),ix)          # get chromosome fitness
        fitness[ix,1] =                                         # store position in population matrix
        
        #if fitness[ix] > maximumFitness:                       # get index of best chromosome
            #maximumFitness = fitness[ix]
            #bestIndividualIndex = ix
    fitness = np.sort(fitness, order = 'fitness')
    wBest = np.array(population[bestIndividualIndex,:])         # store the best chromosome
    
    tempPopulation = np.array(population)

    for i in range(0,popSize,4):                                # only every other individual gets considered
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

# Loop over generations


# write solution
#with open('test_file.csv', 'w') as csvfile:
    #writer = csv.writer(csvfile)
    #[writer.writerow(r) for r in table]
