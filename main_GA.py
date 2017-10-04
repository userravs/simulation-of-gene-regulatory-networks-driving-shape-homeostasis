import time
import random
import numpy as np
from tools_GA import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       PARAMETERS                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
popSize = 30                                                # Population size
nNodes = 10
nGenes = nNodes**2                                          # Number of genes
crossoverProb = 0.8                                         # Crossover probability
mutationProb = 0.025                                        # Mutation probability
crossMutProb = 0.5                                          # probability of doing mutation or crossover
tournamentSelParam = 0.75                                   # Tournament selection parameter
tournamentSize = 4                                          # Tournament size. EVEN
eliteNum = 2                                                # number of elite solutions to carry to next generation
nOfGenerations = 20
timeSteps = 200
nLattice = 50
mode = True
#fitness = np.zeros([popSize,2])                            # fitness array
eliteIndividuals = []
dtype = [('fitnessValue',float),('position',int)]           # format for fitness array, for an easier sort

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       INITIALISATION             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#population = InitializePopulation(popSize, numberOfGenes)  # call initialization function, a random set of chromosomes is generated
population = np.random.random(size = (popSize, nGenes))
contestants = np.zeros([tournamentSize, nGenes])

for iGen in range(nOfGenerations):
    # DEBUG
    print('\nGeneration #' + str(iGen + 1))
    #maxFitness = 0. # Assumes non-negative fitness values!
    fitness = np.zeros(popSize, dtype = dtype)              # structured array which will contain a fitness value for each individual
    #wBest = np.zeros(nGenes) # [0 0]
    #bestIndividualIndex = 0

    # chromosomes get decoded and evaluated
    for ix in range(popSize):
        chromosome = np.array(population[ix,:])             # loop through all chromosomes
        # DEBUG
        #print('=> running system... ' + str(ix) + ' time')
        wMatrix = -1 + 2*chromosome.reshape(nNodes,nNodes)  # decode chromosome, i.e., transform into matrix
        fitness[ix][0] = EvaluateIndividual(wMatrix, timeSteps, iGen, nNodes, ix, nLattice, mode)        # get chromosome fitness
        # DEBUG
        #print('fitness: ' + str(fitness[ix][0]))
        fitness[ix][1] = ix                                 # store position in population matrix
        #[(0.06,0),(0.45,1),(0.21,2)]
    # loop over chromosomes

    fitness.sort(order = 'fitnessValue')                    # sort array according to fitness value. Less fit to most fit

    tempPopulation = np.zeros([popSize, nGenes])           #np.array(population)

    # DEBUG
    #print('sorted fitness array, before deleting:\n' + str(fitness))

    iElit = 1                                                   # Elite counter: individuals with the best fitness are kept untouched
    while iElit <= eliteNum:
        index = fitness[popSize - iElit][1]                     # get the index of the last members of the list, i.e., most fit
        # DEBUG
        #print('=> best fitness: ' + str(fitness[popSize - iElit][0]))
        tempPopulation[iElit - 1,:] = np.array(population[index,:])   # store as part of the new generation of individuals
        #del fitness[popSize - iElit]                            # delete last tuple on the list
        np.delete(fitness,popSize - iElit)
        iElit += 1
    # while

    loopCounter = 0
    while len(fitness) >= tournamentSize:                       # iterate through all individuals
        #print('fitness array length: ' + str(len(fitness)))
        selectedInd = np.random.choice(range(len(fitness)), tournamentSize, replace = False)
        selectedInd.sort()                                      # select random contestants and sort them by index (i.e. by fitness))
        # DEBUG
        #print('selected contestants for tournament:\n' + str(selectedInd))

        # General implementation
        #winIndex = np.zeros([int(tournamentSize/2)])
        #for ik in range(int(tournamentSize/2)):
            #winIndex[ik] = fitness[selectedInd[tournamentSize - 1 - ik]][1]   # the fittest ind are retrieved from the sorted fitness array
            #contestants[ik,:] = np.array(population[winIndex[ik],:])


        # hardcoded for performance gain
        winIndex1 = fitness[selectedInd[tournamentSize - 1]][1]   # the fittest ind are retrieved from the sorted fitness array
        contestants[0,:] = np.array(population[winIndex1,:])
        winIndex2 = fitness[selectedInd[tournamentSize - 2]][1]   # the fittest ind are retrieved from the sorted fitness array
        contestants[1,:] = np.array(population[winIndex2,:])

        r = np.random.random()
        if r >= crossMutProb:
            contestants[2,:],contestants[3,:] = Crossover(contestants[0,:], contestants[1,:])
        else:
            contestants[2,:],contestants[3,:] = Mutate(np.array(contestants[0,:]), np.array(contestants[1,:]))

        iCounter = 0
        for ix in selectedInd:
            fitness = np.delete(fitness,ix - iCounter)
            iCounter += 1
        # DEBUG
        #print('sorted fitness array, after deleting:\n' + str(fitness))

        for jk in range(tournamentSize):
            index = eliteNum + (loopCounter*tournamentSize) + jk
            #print('=> elitNum: ' + str(eliteNum) + ', loopCounter: ' + str(loopCounter) + ', jk: ' + str(jk))
            tempPopulation[index] = contestants[jk,:]
        loopCounter += 1
    # loop over population

    population = np.array(tempPopulation)

# Loop over generations


# write solution
bestIndEver = np.array(population[0,:].reshape(nNodes,nNodes))
with open('test_file.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    [writer.writerow(r) for r in population]
