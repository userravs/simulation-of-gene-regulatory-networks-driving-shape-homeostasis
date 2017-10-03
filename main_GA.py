import time
import random 
import numpy as np
from tools_GA import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       PARAMETERS                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
popSize = 30                                                # Population size
nNodes = 25
nGenes = nNodes**2                                          # Number of genes
crossoverProb = 0.8                                         # Crossover probability
mutationProb = 0.025                                        # Mutation probability
crossMutProb = 0.5                                          # probability of doing mutation or crossover
tournamentSelParam = 0.75                                   # Tournament selection parameter
tournamentSize = 4                                          # Tournament size. EVEN                        
eliteNum = 6                                                # number of elite solutions to carry to next generation
nOfGenerations = 200
#fitness = np.zeros([popSize,2])                            # fitness array
eliteIndividuals = []
dtype = [('fitnessValue',float),('position',int)]           # format for fitness array, for an easier sort

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       INITIALISATION             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#population = InitializePopulation(popSize, numberOfGenes)  # call initialization function, a random set of chromosomes is generated
population = np.random.random(size = (popSize, nGenes))
#contestants = np.zeros([tournamentSize, nGenes])

for iGen in range(nOfGenerations):
    #maxFitness = 0. # Assumes non-negative fitness values!
    fitness = np.zeros(popsize, dtype = dtype)              # structured array which will contain a fitness value for each individual
    #wBest = np.zeros(nGenes) # [0 0]
    #bestIndividualIndex = 0

    # chromosomes get decoded and evaluated
    for ix in range(popSize):
        chromosome = np.array(population[ix,:])             # loop through all chromosomes
        wMatrix = -1 + 2*chromosome.reshape(nNodes,nNodes)  # decode chromosome, i.e., transform into matrix
        fitness[ix][0] = EvaluateIndividual(wMatrix)        # get chromosome fitness
        fitness[ix][1] = ix                                 # store position in population matrix
    # loop over chromosomes
    
        #if fitness[ix] > maximumFitness:                   # get index of best chromosome
            #maximumFitness = fitness[ix]
            #bestIndividualIndex = ix
    fitness.sort(order = 'fitnessValue')                    # sort array according to fitness value. Less fit to most fit
    #wBest = np.array(population[bestIndividualIndex,:])     # store the best chromosome
    
    tempPopulation = np.zeros(size = (popsize, nGenes))           #np.array(population)

    iElit = 1                                                   # Elite counter: individuals with the best fitness are kept untouched 
    while iElit <= elitNum:                                      
        index = fitness[popSize - iElit][1]                     # get the index of the last members of the list, i.e., most fit
        tempPopulation[iElit - 1] = np.array(population[index,:])   # store as part of the new generation of individuals   
        #del fitness[popSize - iElit]                            # delete last tuple on the list
        np.delete(fitness,popSize - iElit)
        iElit += 1                                  
    # while   

    while len(fitness) >= tournamentSize:                       # iterate through all individuals 
        selectedInd = np.random.choice(range(len(fitness)), tournamentSize, replace = False)
        selectedInd.sort()                                      # select random contestants and sort them by index (i.e. by fitness))

        for ik in range(tournamentSize):
            winIndex1 = fitness[selectedInd[tournamentSize - 1]][1]   # the fittest individuals are retrieved from the sorted fitness array
            winIndex2 = fitness[selectedInd[tournamentSize - 2]][1]

            winInd1 = np.array(population[winIndex1,:])
            winInd2 = np.array(population[winIndex2,:])

        contestants[0,:] = winInd1      # WARNING might be unncesessary to copy this arrays everywhere
        contestants[1,:] = winInd2
        #contestants[2,:],contestants[3,:] = GetOffspring(winInd1, winInd2, crossoverProb, mutationProb)
        
        r = np.random.random()
        if r >= crossMutProb: 
            contestants[2,:],contestants[3,:] = Crossover(winInd1, winInd2, crossoverProb)
        else:
            contestants[2,:],contestants[3,:] = Mutation(winInd1, winInd2, mutationProb)

        for ix in selectedInd:
            np.delete(fitness,ix)


    # WARNING initial implementation, not really working...
    #while len(fitness) >= tournamentSize:
        #selectedInd = np.zeros([tournamentSize])                # array to store selected indexes
        #for ik in range(tournamentSize):
            #randomSelection = np.random.randint(len(fitness))   # generate random index
            #selectedInd[ik] = fitness[randomSelection][1]       # save pos in population matrix
            #np.delete(fitness,randomSelection)                  # delete entry
        
        ##selectedInd = np.random.randint(len(fitness),size = 4) # random positions of
        #selectedInd.sort()                                      # sort indexes, from 
        #for ik in range(tournamentSize):
            #index = eliteNum + ik                               # generate index where the winning individual will be stored in the newpop array
            #if ik < int(tournamentSize/2):                      # check first two individuals
                #winningInd = selectedInd[tournamentSize - 1 - ik]   # last two indexes in the sorted array
                #tempPopulation[index] = np.array(population[winningInd,:])
        
    # WARNING Code from SOA
    #for iInd in range(len(fitness)-1,-1,-1):
        #if iPos < 6:
            #index = fitness[iInd][1]
            #tempPopulation[iPos] = np.array(population[index,:])
            #iPos += 1
    #for i in range(0,popSize,4):                                # only every other individual gets considered
        #i1 = TournamentSelect(fitness,tournamentSelParam)
        #i2 = TournamentSelect(fitness,tournamentSelParam)
        #chromosome1 = population[i1,:]
        #chromosome2 = population[i2,:]
        #tempPopulation[i,:] = chromosome1
        #tempPopulation[i+1,:] = chromosome2

        #r = np.random.random()
        #if r < crossProb:
            #newChromosomePair = Cross(chromosome1,chromosome2)
            #tempPopulation[i,:] = newChromosomePair[1,:]
            #tempPopulation[i+1,:] = newChromosomePair[2,:]
        #else:
            #tempPopulation[i,:] = chromosome1
            #tempPopulation[i+1,:] = chromosome2
    ## Loop over population

    #for i in range(popSize):
        #originalChromosome = tempPopulation[i,:]
        #mutatedChromosome = Mutate(originalChromosome,mutProb)
        #tempPopulation[i,:] = mutatedChromosome

    #tempPopulation[1,:] = population[bestIndividualIndex,:]
    population = np.array(tempPopulation)

# Loop over generations


# write solution
#with open('test_file.csv', 'w') as csvfile:
    #writer = csv.writer(csvfile)
    #[writer.writerow(r) for r in table]
