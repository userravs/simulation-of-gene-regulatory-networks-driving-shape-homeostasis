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
#    	Functions                  #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#    	PARAMETERS                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
nLattice = 100                              # TODO change name
timeSteps = 200                              # Number of simulation time steps
cellGrid = np.zeros([nLattice,nLattice,3])  # Initialize empty grid
SGF_read = 0                                # in the future values will be read from the grid
LGF_read = 0
ix = int(nLattice/2)                        # Initial position for the mother cell
iy = int(nLattice/2)
cellList = []

# create mother cell and update the grid with its initial location
cellList.append(cell(ix,iy))
cellGrid[ix][iy][0] = 1
#agentsGrid = cellGrid[:,:,0]               # slice the grid to get the layer with the cell positions
#sgfGrid = cellGrid[:,:,1]                  # slice the grid to get the layer with the cell positions
#lgfGrid = cellGrid[:,:,2]                  # slice the grid to get the layer with the cell positions

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
    
    tmpCellList = list(cellList)                                # a copy of the list of current cells is used to iterate over all the cells
    
    while len(tmpCellList) > 0:                                 # while  the tmp list of cells is longer than 1
        rndCell = np.random.randint(len(tmpCellList))           # choose a random cell in the list of existing cells
        # random cell should decide and action
        tmpCellList[rndCell].border = nLattice
        # first update cell status
        tmpCellList[rndCell].GenerateStatus(SGF_read, LGF_read) # get status of this cell

        # DEBUG
        print('cell number: ' + str(len(cellList)) + '\nCell status: ' + str(tmpCellList[rndCell].state))# + '\n')
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #        Cell Action                #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#        
        # according to cell status perform action: split or stay quiet
        if tmpCellList[rndCell].state == 'Quiet':       # Check the state
            tmpCellList[rndCell].Quiet()                # call method that performs selected action
            tmpCellList[rndCell].sgfProduce(cellGrid)
            tmpCellList[rndCell].lgfProduce(cellGrid)
            del tmpCellList[rndCell]                    # delete cell from temporal list
         
        elif tmpCellList[rndCell].state == 'Split':
            tmpCellList[rndCell].Split2(cellGrid,cellList)
            tmpCellList[rndCell].sgfProduce(cellGrid)
            tmpCellList[rndCell].lgfProduce(cellGrid)
            del tmpCellList[rndCell]

        elif tmpCellList[rndCell].state == 'Move':
            tmpCellList[rndCell].Move2(cellGrid)
            del tmpCellList[rndCell]
         
	# WARNING see TODO
        else: # Die
            tmpCellList[rndCell].dieCounter += 1
            if tmpCellList[rndCell].dieCounter == tmpCellList[rndCell].dieTime:
                tmpCellList[rndCell].Die(cellGrid)      # Off the grid
                del tmpCellList[rndCell]
                # TODO this way of killing the cell doesn't work, cellList and tmpCellList not necesarily have the same length 
                del cellList[rndCell]                   # Actual death                

    ### TEST! equivalent to: cellList[cell].'status'(param_x,param_y)
    #    state = getattr(tmpCellList[rndCell], status)
    #    action = getattr(tmpCellList[rndCell], state)
    #    action(cellGrid, cellList)
    # while

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
                lgfPlot)

    itime += 1

# while    

print(str(timeSteps)+' time steps complete')

#if __name__ == '__main__':
#    main()
