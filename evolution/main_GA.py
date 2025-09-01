import sys                                  # to get command line args
import os                                   # to handle paths
import time                                 # to get system time
from datetime import datetime as dt
#import random                   
import numpy as np  
from tools_GA import *
############
# self made classes
from core.cell_agent import *                    # it is allowed to call from this class because there's an __init__.py file in this directory
from core.tools import *
from visualization.plot import *
import csv
############
import multiprocessing as mp
import ctypes
#from numba import jit
from contextlib import contextmanager
from functools import partial

#============================================================#
#                                                            #
#                   CELLULAR AUTOMATA                        #
#                                                            #
#============================================================#
#@jit
def sim(wMatrix, timeSteps, iGen, nNodes, individual, nLattice, mode):
    """
    Parameters: sim(wMatrix, numberOfTimeSteps, NumberOfGeneration, nNodes, individual, nLattice, mode)
    # mode = True: cell_system as fitness function
    # mode = False: cell_system as display system
    """
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #           PARAMETERS              #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # TODO: organize in different categories...
    #nLattice = 5                               # TODO change name
    #timeSteps = 40                             # Number of simulation time steps
    cellGrid = np.zeros([nLattice,nLattice,3])  # Initialize empty grid
    SGF_read = 0.                               # in the future values will be read from the grid
    LGF_read = 0.
    ix = int(nLattice/2)                        # Initial position for the mother cell
    iy = int(nLattice/2)                        # Initial position for the mother cell
    iTime = 0                                   # time counter

    cellList = []                               # List for cell agents

    # SGF/LGF dynamics parameters
    deltaT = 1.                                 # time step for discretisation [T]
    deltaR = 1.                                 # space step for discretisation [L]
    deltaS = 0.5                                # decay rate for SGF
    deltaL = 0.1                                # decay rate for LGF
    diffConst = 1.#0.05                         # diffusion constant D [dimentionless]
    t_matrix = GenerateTMatrix(nLattice)        # T matrix for LGF operations
    i_matrix = GenerateIMatrix(nLattice)        # I matrix for LGF operations

    # timing variables!
    tmpListLoopAvg = 0
    chemicalsUpdateAvg = 0

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #       INITIALIZATION             #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # create mother cell and update the grid with its initial location
    cellList.append(cell(ix,iy,wMatrix,nNodes))
    cellGrid[ix][iy][0] = 1
    #print('Initial grid:\n' + str(cellGrid[:,:,0]))
    #cellGrid[ix][iy][2] = 400.

    # Timing!
    #start_time_figurecall = time.time()
    # Plot figure and subplots
    #cellsFigure, cellsSubplot, sgfSubplot, lgfSubplot, cellPlot, sgfPlot, lgfPlot = Environment.CellsGridFigure(nLattice, mode)
    #end_time_figurecall = time.time()
    #secs = end_time_figurecall - start_time_figurecall

    #print('time to call figures, subplots, plots:' + str(secs))
    # DEBUG
    #print('Time running...')
    # Timing!
    start_time_mainLoop = time.time()
    while iTime < timeSteps:
        # DEBUG
        #print('\n######### time step #' + str(iTime))

        ## decay chemicals in spots where there is some but no cell

        # this matrixes must be updated everytime so that if there's no production in one spot that spot contains a zero
        # but must not lose contained information, i.e. must use it before setting it to zero
        sigma_m = np.zeros([nLattice,nLattice])     # matrix representation of SGF production
        lambda_m = np.zeros([nLattice,nLattice])    # matrix representation of LGF production

        tmpCellList = list(cellList)                                  # a copy of the list of current cells is used to iterate over all the cells

        # Timing!
        start_time_tmpListLoop = time.time()
        tmpCellListLength = len(tmpCellList)
        while len(tmpCellList) > 0:                                     # while  the tmp list of cells is longer than 1
            # 1st step => choose a random cell from the list of existing cells
            rndCell = np.random.randint(len(tmpCellList))
            # store lattice size
            tmpCellList[rndCell].border = nLattice                      # TODO rethink this
            #tmpCellList[rndCell].nNodes = nNodes                       # WARNING hardcoded

            # 2nd step => read chemicals
            SGF_reading, LGF_reading = tmpCellList[rndCell].Sense(cellGrid)

            # 3rd step => random cell should decide and action
            tmpCellList[rndCell].GenerateStatus(SGF_reading, LGF_reading)     # get status of this cell

            # 4th step => update SGF and LGF amounts on the 'production' matrices sigma & lambda
            # production matrices get updated values
            sigma_m[tmpCellList[rndCell].yPos,tmpCellList[rndCell].xPos] = tmpCellList[rndCell].sgfAmount
            lambda_m[tmpCellList[rndCell].yPos,tmpCellList[rndCell].xPos] = tmpCellList[rndCell].lgfAmount

            # DEBUG
            #print('\ncell number: ' + str(len(cellList)) + '\nCell status: ' + str(tmpCellList[rndCell].state))# + '\n')
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            #        Cell Action            #
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            # according to cell status perform action: split or stay quiet
            if tmpCellList[rndCell].state == 'Quiet':                   # Check the state
                tmpCellList[rndCell].Quiet(cellGrid)                    # call method that performs selected action
                del tmpCellList[rndCell]                                # delete cell from temporal list

            elif tmpCellList[rndCell].state == 'Split':
                tmpCellList[rndCell].Split(cellGrid,cellList)
                del tmpCellList[rndCell]

            elif tmpCellList[rndCell].state == 'Move':
                tmpCellList[rndCell].Move(cellGrid)
                del tmpCellList[rndCell]

            else: # Die
                tmpCellList[rndCell].Die(cellGrid)                  # Off the grid, method also changes the "amidead" switch to True
                del tmpCellList[rndCell]
        # while
        # Timing!
        end_time_tmpListLoop = time.time()
        secs = end_time_tmpListLoop - start_time_tmpListLoop
        #print('time taken through cells: {:.3f}, number of cells: {:.3f}'.format(secs, tmpCellListLength))

        # A list of cells that "died" is stored to later actually kill the cells...
        listLength = len(cellList) - 1
        for jCell in range(listLength,-1,-1):                     # checks every cell and if it was set to die then do, in reverse order
            #print('len(cellList): ' + str(len(cellList)) + '. Current element: ' + str(jCell))
            if cellList[jCell].amidead:
                del cellList[jCell]

        ### TEST! equivalent to: cellList[cell].'status'(param_x,param_y)
        #    state = getattr(tmpCellList[rndCell], status)
        #    action = getattr(tmpCellList[rndCell], state)
        #    action(cellGrid, cellList)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #    SGF/LGF diffusion and/or decay     #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # Timing!
        #start_time_chemicalsUpdate = time.time()
        cellGrid[:,:,1] = SGFDiffEq(cellGrid[:,:,1], sigma_m, deltaS, deltaT)
        cellGrid[:,:,2] = LGFDiffEq(i_matrix, t_matrix, cellGrid[:,:,2], lambda_m, deltaL, deltaT, deltaR, diffConst)
        # Timing!
        #end_time_chemicalsUpdate = time.time()
        #secs = end_time_chemicalsUpdate - start_time_chemicalsUpdate
        #print('time taken to update chemicals:' + str(secs))
        #chemicalsUpdateAvg += secs

        #chemsum = 0
        #for iPos in range(nLattice):
            #for jPos in range(nLattice):
                #chemsum += cellGrid[iPos,jPos,2]
                #if cellGrid[iPos,jPos,2] < 0.01:
                    #cellGrid[iPos,jPos,2] = 0
        #print('grid after update...\n' + str(cellGrid[:,:,2]))
    #    print('################################LGF total = ' + str(chemsum))
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #         Plot               #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #print('updated grid:\n' + str(cellGrid[:,:,0]))

        if mode == True:
            if len(cellList) == 0:                                      # if cells die during the simulation resturn two different structs
                halfwayStruct = np.zeros([nLattice,nLattice])
                finalStruct = np.ones([nLattice,nLattice])
                break
            elif iTime == int(timeSteps/2) - 1:                             # special cases get tested halfway through the simulation
                if len(cellList) <= int((nLattice**2)*0.01):                                  # If there are no cells 
                    halfwayStruct = np.zeros([nLattice,nLattice])       # return two completely different structure matrices to get 0 fitness
                    finalStruct = np.ones([nLattice,nLattice])
                    break
                else:
                    halfwayStruct = np.array(cellGrid[:,:,0])
        #         Environment.AntGridPlot(cellGrid,
        #                                 nLattice,
        #                                 cellsFigure,
        #                                 cellsSubplot,
        #                                 sgfSubplot,
        #                                 lgfSubplot,
        #                                 cellPlot,
        #                                 sgfPlot,
        #                                 lgfPlot,
        #                                 iTime,
        #                                 iGen,
        #                                 individual,
        #                                 mode)
        #
            elif iTime == timeSteps - 1:
                if len(cellList) == nLattice**2:                      # If cells fill space 
                    halfwayStruct = np.zeros([nLattice,nLattice])       # return two completely different structure matrices to get 0 fitness
                    finalStruct = np.ones([nLattice,nLattice])
                    # break
                else:
                    finalStruct = np.array(cellGrid[:,:,0])
        #         Environment.AntGridPlot(cellGrid,
        #                                 nLattice,
        #                                 cellsFigure,
        #                                 cellsSubplot,
        #                                 sgfSubplot,
        #                                 lgfSubplot,
        #                                 cellPlot,
        #                                 sgfPlot,
        #                                 lgfPlot,
        #                                 iTime,
        #                                 iGen,
        #                                 individual,
        #                                 mode)
        else:
            # Timing!
            #start_time_plotUpdate = time.time()
            Environment.AntGridPlot(    cellGrid,
                                        nLattice,
                                        cellsFigure,
                                        cellsSubplot,
                                        sgfSubplot,
                                        lgfSubplot,
                                        cellPlot,
                                        sgfPlot,
                                        lgfPlot,
                                        iTime,
                                        iGen,
                                        individual,
                                        mode)
            # Timing!
        #     end_time_plotUpdate = time.time()
        #     secs = end_time_plotUpdate - start_time_plotUpdate
        #     #print('time taken to update plots:' + str(secs))
        #     time.sleep(0.1)
        iTime += 1

    # while
    # Timing!
    end_time_mainLoop = time.time()
    secs = end_time_mainLoop - start_time_mainLoop
    tmpListLoopAvg += secs
    
    #print('\ntime taken in main loop:' + str(secs))

    #print('\ntime taken in timeSteps: {:.5f} s'.format(secs))
    #print('Avg time updating chemicals: {:.5f} ms'.format(chemicalsUpdateAvg*1000/timeSteps))
    print('Avg time looping through cells: {:.3f} s, total: {:.3f} s'.format(tmpListLoopAvg/timeSteps, tmpListLoopAvg))

    # DEBUG
    # print(str(timeSteps)+' time steps complete')

    # Timing!
    #start_time_finalFunctions = time.time()

    halfwayStruct = GetStructure(halfwayStruct, nLattice)
    finalStruct = GetStructure(finalStruct, nLattice)

    deltaMatrix = np.zeros([nLattice,nLattice])
    for ik in range(nLattice):
        for jk in range(nLattice):
            if halfwayStruct[ik,jk] != finalStruct[ik,jk]:
                deltaMatrix[ik,jk] = 1
    # Timing!
    #end_time_finalFunctions = time.time()
    #secs = end_time_finalFunctions - start_time_finalFunctions
    #print('\ntime taken to get delta matrix:' + str(secs))


    # DEBUG
    #print('half way structure:\n' + str(halfwayStruct))
    #print('final structure:\n' + str(finalStruct))
    #print('delta matrix:\n' + str(deltaMatrix))
    
    if mode:
        return deltaMatrix

#@jit
def EvaluateIndividual(individual, timeSteps, iGen, nNodes, nLattice, mode):
    totSum = 0.
    #print('generating wMatrix...')
    wMatrix = population[individual,:].reshape(nNodes,nNodes)
    #print('process: {} is running sim  with individual: {}!'.format(os.getpid(), individual))
    # Timing!
    start_time_chemicalsUpdate = time.time()
    deltaM = sim(wMatrix, timeSteps, iGen, nNodes, individual, nLattice, mode)    # Timing!
    end_time_chemicalsUpdate = time.time()
    secs = end_time_chemicalsUpdate - start_time_chemicalsUpdate
    print('Proc {}: Time taken to run sim: {:.3f}'.format(os.getpid(), secs))
    #print('process: {} done with individual: {}!'.format(os.getpid(), individual))
    deltaMatrix = np.array(deltaM)
    #m, n = deltaMatrix.shape()
    #m = 50
    for ix in range(nLattice):
        for jx in range(nLattice):
            totSum += deltaMatrix[ix,jx]
    #print('max score: {}, totsum = {}'.format(nLattice**2, totSum))
    # DEBUG
    #print('total sum on delta matrix: ' + str(totSum))
    #if totSum <= int((nLattice**2)*0.1) or totSum == int(nLattice**2):
        #fitness[individual] = 0.
    #else:
        #fitness[individual] = 1. - (1./(nLattice**2))*totSum
    fitness[individual] = 1. - (1./(nLattice**2))*totSum
    #print('fitness = {:.3f}'.format(fitness[individual]))
    return fitness
# EvaluateIndividual

#============================================================#
#                                                            #
#                   GENETIC ALGORITHM                        #
#                                                            #
#============================================================#
if __name__ == '__main__':
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #       PARAMETERS                 #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # nProcs*cycles = 4*int + 2
    # popSize = nProcs*cycles
    nProcs = 2   #11                             # multiprocessing will use as many cores as it can see
    DEFAULT_VALUE = -1                                          # WARNING
    popSize = 6                           # Population size
    nNodes = 25
    nGenes = nNodes**2                                          # Number of genes
    crossoverProb = 1. #0.8                                     # Crossover probability
    mutationProb = 1. #0.5                                      # Mutation probability
    crossMutProb = 0.5                                          # probability of doing mutation or crossover
    #tournamentSelParam = 0.75                                  # Tournament selection parameter
    tournamentSize = 4                                          # Tournament size. EVEN
    eliteNum = 2                                                # number of elite solutions to carry to next generation
    nOfGenerations = 15
    timeSteps = 200
    nLattice = 50
    mode = True
    fileName = sys.argv[1] #'benchmark_test_ozzy_20171015_crossP1a'
    chunkSize = 1                                              # TEST 
    
    # timing variables!
    generationAvg = 0

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #       INITIALISATION             #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #population = InitializePopulation(popSize, numberOfGenes)  # call initialization function, a random set of chromosomes is generated
    #population = np.random.random(size = (popSize, nGenes))
    contestants = np.zeros([tournamentSize, nGenes])
    fitnessInfo = np.zeros([nOfGenerations, 2])


    print('Parameters: \nFile name: {}\nnProcs = {}, Population size = {}, nNodes = {}, nLattice = {}, nGen = {}, Crossover Prob = {}, Mutation prob = {}'.format(fileName, nProcs, popSize, nNodes, nLattice, nOfGenerations, crossoverProb, mutationProb))

    # multiprocessing implementation
    population_base = mp.Array(ctypes.c_float, popSize*nGenes, lock = False)    # create mp shared array
    #print('population_base length: {}'.format(len(population_base)))
    population = np.frombuffer(population_base, dtype = ctypes.c_float)         # convert mp array to np.array
    population = population.reshape(popSize, nGenes)
    #print('population length: {}'.format(len(population)))
    
    randPop = np.random.rand(popSize, nGenes)
    np.copyto(population, randPop)
    
    #for ix in range(popSize*nGenes):
        #population[ix] = -1. + 2.*np.random.random()                            # Generate population
    #print('population shared array created successfully!')

    fitness_base = mp.Array(ctypes.c_float, popSize, lock = False)              # create mp shared array
    fitness = np.frombuffer(fitness_base, dtype = ctypes.c_float)               # convert mp array to np.array
    #print('fitness shared array created successfully!')

    for iGen in range(nOfGenerations):
        # Timing!
        start_time_generation = time.time()
        # DEBUG
        print('\nGeneration #' + str(iGen + 1))

        # 1st step: Fitness function => Rank idividuals by their fitness
        # chromosomes get decoded and evaluated
        #for ix in range(popSize):
            #chromosome = np.array(population[ix,:])             # loop through all chromosomes
            ## DEBUG
            #print('=> running system... ' + str(ix) + ' time')
            #wMatrix = -1 + 2*chromosome.reshape(nNodes,nNodes)  # decode chromosome, i.e., transform into matrix

            ##fitness[ix][0] = EvaluateIndividual(wMatrix, timeSteps, iGen, nNodes, individual, nLattice, mode)        # get chromosome fitness
            #fitness = EvaluateIndividual(ix, timeSteps, iGen, nNodes, nLattice, mode)

            ## DEBUG
            #print('fitness: ' + str(fitness[ix][0]))
            ##fitness[ix][1] = ix                                 # store position in population matrix
        ## loop over chromosomes

        # multiprocess implementation!

        fitness.fill(DEFAULT_VALUE)
        timeSteps_list = [timeSteps for x in range(popSize)]
        iGen_list = [iGen for x in range(popSize)]
        nNodes_list = [nNodes for x in range(popSize)]
        nLattice_list = [nLattice for x in range(popSize)]
        mode_list = [mode for x in range(popSize)]
        index_list = [x for x in range(popSize)]
        args = zip(index_list, timeSteps_list, iGen_list, nNodes_list, nLattice_list, mode_list)

        # Timing!
        start_time_fitness = time.time()
        with mp.Pool(processes = nProcs) as pool:
            pool.starmap(EvaluateIndividual, args, chunkSize)              # Evaluation of individuals, this runs in parallel!
        
        end_time_fitness = time.time()
        secs = end_time_fitness - start_time_fitness
        
        #pool = multiprocessing.Pool(processes=NBR_OF_PROCESSES)
        #print('creating pool...')
        #pool = mp.Pool(processes = nProcs)
        #print('evaluating pool...')
        # Timing!
        #start_time_fitness = time.time()
        #pool.starmap(EvaluateIndividual, args, chunkSize)
        # Timing!
        #end_time_fitness = time.time()
        #secs = end_time_fitness - start_time_fitness
        ####

        # 1.1: sort fitness array
        #fitness.sort(order = 'fitnessValue')                    # sort array according to fitness value. Less fit to most fit
        sorted_fitness = np.argsort(fitness)
        tempPopulation = np.zeros([popSize, nGenes])            #np.array(population)
        
                # 1.2: get fittest infividual and mean fitness
        fitnessInfo[iGen, 0] = np.amax(fitness) #sorted_fitness[popSize - 1]                   # np.amax(fitness)
        fitnessInfo[iGen, 1] = np.average(fitness)
        print('Gen: {1}, max fit: {2:.3f}, avg fit: {0:.3f}'.format(np.average(fitness), iGen + 1, fitness[sorted_fitness[popSize - 1]]))

        # DEBUG
        #print('sorted fitness array, before deleting:\n' + str(fitness))

        # 2nd step: Elitism => Save the best individuals for next generation
        iElit = 1                                               # Elite counter: individuals with the best fitness are kept untouched
        while iElit <= eliteNum:
            #index = fitness[popSize - iElit][1]                 # get the index of the last members of the list, i.e., most fit
            index = sorted_fitness[popSize - iElit]
            # DEBUG
            #print('=> best fitness: ' + str(fitness[popSize - iElit][0]))
            tempPopulation[iElit - 1,:] = np.array(population[index,:])   # store as part of the new generation of individuals
            #del fitness[popSize - iElit]                       # delete last tuple on the list
            np.delete(sorted_fitness,popSize - iElit)
            iElit += 1
        # while

        # 3rd step: Tousnament selection => Loop over the rest of the population to engage them into a tournament
        loopCounter = 0
        while len(sorted_fitness) >= tournamentSize:                   # iterate through all individuals
            #print('fitness array length: ' + str(len(fitness)))
            selectedInd = np.random.choice(range(len(sorted_fitness)), tournamentSize, replace = False)
            selectedInd.sort()                                  # select random contestants and sort them by index (i.e. by fitness))
            # DEBUG
            #print('selected contestants for tournament:\n' + str(selectedInd))

            # General implementation
            #winIndex = np.zeros([int(tournamentSize/2)])
            #for ik in range(int(tournamentSize/2)):
                #winIndex[ik] = fitness[selectedInd[tournamentSize - 1 - ik]][1]   # the fittest ind are retrieved from the sorted fitness array
                #contestants[ik,:] = np.array(population[winIndex[ik],:])

            # hardcoded for performance gain
            winIndex1 = sorted_fitness[selectedInd[tournamentSize - 1]] # the fittest ind is retrieved from the sorted fitness array
            contestants[0,:] = np.array(population[winIndex1,:])
            winIndex2 = sorted_fitness[selectedInd[tournamentSize - 2]] # the second fittest ind is retrieved from the sorted fitness array
            contestants[1,:] = np.array(population[winIndex2,:])

            # 3.1 step => Generate new offsprig by Crossover or mutation
            r = np.random.random()
            if r >= crossMutProb:
                contestants[2,:],contestants[3,:] = Crossover(contestants[0,:], contestants[1,:], crossoverProb)
            else:
                contestants[2,:],contestants[3,:] = Mutate(np.array(contestants[0,:]), np.array(contestants[1,:]), mutationProb)

            # 3.2 => Delete contestants from fitness array
            iCounter = 0
            for ix in selectedInd:
                index = ix - iCounter
                # DEBUG
                #print('deleting ' + str(index) + ' entry:' + str(fitness[index]))
                sorted_fitness = np.delete(sorted_fitness, index)      # WARNING does this really work?
                iCounter += 1
            # DEBUG
            #print('sorted fitness array, after deleting:\n' + str(fitness))

            # 3.3 => Save best individuals and offspring for new generation
            for jk in range(tournamentSize):
                index = eliteNum + (loopCounter*tournamentSize) + jk
                #print('=> elitNum: ' + str(eliteNum) + ', loopCounter: ' + str(loopCounter) + ', jk: ' + str(jk))
                tempPopulation[index] = contestants[jk,:]
            loopCounter += 1
        # loop over population

        population = np.array(tempPopulation)

        # Timing!
        end_time_generation = time.time()
        secs = end_time_generation - start_time_generation
        generationAvg += secs
        #print('time: {} m, {:.3f} s'.format(int(secs/60), 60*((secs/60)-int(secs/60))))
        print('Time to complete generation: {} m {:.3f} s'.format(int(secs/60), 60*((secs/60)-int(secs/60))))
    # Loop over generations

    print('avg time per generation: {} m {:.3f} s'.format(int(generationAvg/nOfGenerations/60), 60*((generationAvg/nOfGenerations/60)-int(generationAvg/nOfGenerations/60))))
    #print('avg time for generation: {:.3f} s'.format(generationAvg/nOfGenerations))

    # write solution
    with open(fileName + '.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        [writer.writerow(r) for r in population]
    #with open(fileName + '_metadata' + '.csv', 'w') as csvfile:
