#from PyQt4 import QtGui, QtCore
import time
import random 
import numpy as np
import matplotlib.pyplot as plt
# self made classes
from cell_agent import *                    # it is allowed to call from this class because there's an __init__.py file in this directory
from tools import *
from plot import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       Functions                  #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       PARAMETERS                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
nLattice = 50                              # TODO change name
timeSteps = 200                              # Number of simulation time steps
cellGrid = np.zeros([nLattice,nLattice,3])  # Initialize empty grid
SGF_read = 0                                # in the future values will be read from the grid
LGF_read = 0
ix = int(nLattice/2)                        # Initial position for the mother cell
iy = int(nLattice/2)
cellList = []
deltaT = 1
deltaS = 0.5
# create mother cell and update the grid with its initial location
cellList.append(cell(ix,iy))
cellGrid[ix][iy][0] = 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#    	INITIALIZATION             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Plot figure and subplots
cellsFigure, cellsSubplot, sgfSubplot, lgfSubplot, cellPlot, sgfPlot, lgfPlot = Environment.CellsGridFigure(nLattice)

itime = 0

# DEBUG
print('Time running...')

while itime < timeSteps:
    # DEBUG 
    print('\ntime step #' + str(itime))
    
    tmpCellList = list(cellList)                                    # a copy of the list of current cells is used to iterate over all the cells
    while len(tmpCellList) > 0:                                     # while  the tmp list of cells is longer than 1
        rndCell = np.random.randint(len(tmpCellList))               # choose a random cell in the list of existing cells
        # random cell should decide and action
        tmpCellList[rndCell].border = nLattice                      # store lattice size
        SGF_reading, LGF_reading = tmpCellList[rndCell].Sense(cellGrid)     # read chemicals
        # first update cell status
        tmpCellList[rndCell].GenerateStatus(SGF_read, LGF_read)     # get status of this cell

        # DEBUG
        print('cell number: ' + str(len(cellList)) + '\nCell status: ' + str(tmpCellList[rndCell].state))# + '\n')
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #        Cell Action                #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#        
        # according to cell status perform action: split or stay quiet
        if tmpCellList[rndCell].state == 'Quiet':                   # Check the state
            tmpCellList[rndCell].Quiet(cellGrid)                    # call method that performs selected action
            cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)            
#            tmpCellList[rndCell].sgfProduce(cellGrid)
            tmpCellList[rndCell].lgfProduce(cellGrid)
            del tmpCellList[rndCell]                                # delete cell from temporal list
         
        elif tmpCellList[rndCell].state == 'Split':
            tmpCellList[rndCell].Split2(cellGrid,cellList)
            cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)
#            tmpCellList[rndCell].sgfProduce(cellGrid)
            tmpCellList[rndCell].lgfProduce(cellGrid)
            del tmpCellList[rndCell]

        elif tmpCellList[rndCell].state == 'Move':
            tmpCellList[rndCell].Move2(cellGrid)
            cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)
            del tmpCellList[rndCell]
         
        else: # Die
            tmpCellList[rndCell].dieCounter += 1
            if tmpCellList[rndCell].dieCounter == tmpCellList[rndCell].dieTime:
                tmpCellList[rndCell].Die(cellGrid)                  # Off the grid, method also changes the "amidead" switch to True
                cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, 0, deltaS, deltaT)
                del tmpCellList[rndCell]
            else:
                cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)
        
        # after the cell reads the grid and performs an action the pheromone is updated according to the diff eq
        
    # while

    # A list of cell that "died" is stored to later actually kill the cells...
    listLength = len(cellList) - 1
    for jCell in range(listLength,-1,-1):                     # checks every cell and if it was set to die then do, in reverse order
        #print('len(cellList): ' + str(len(cellList)) + '. Current element: ' + str(jCell))
        if cellList[jCell].amidead:
            print('cell died!')
            del cellList[jCell]
    
    ### TEST! equivalent to: cellList[cell].'status'(param_x,param_y)
    #    state = getattr(tmpCellList[rndCell], status)
    #    action = getattr(tmpCellList[rndCell], state)
    #    action(cellGrid, cellList)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #        Plot                #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    Environment.AntGridPlot(cellGrid,
                nLattice,
                cellsFigure, 
                cellsSubplot, 
                sgfSubplot, 
                lgfSubplot, 
                cellPlot, 
                sgfPlot, 
                lgfPlot,itime)

    itime += 1
    
# while    

print(str(timeSteps)+' time steps complete')

# TODO look this up
#if __name__ == '__main__':
#    main()
