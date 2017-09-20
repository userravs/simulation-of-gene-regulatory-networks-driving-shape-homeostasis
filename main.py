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
#       PARAMETERS                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
nLattice = 10                              # TODO change name
timeSteps = 50                              # Number of simulation time steps
cellGrid = np.zeros([nLattice,nLattice,3])  # Initialize empty grid
SGF_read = 0                                # in the future values will be read from the grid
LGF_read = 0
ix = int(nLattice/2)                        # Initial position for the mother cell
iy = int(nLattice/2)                        # Initial position for the mother cell
cellList = []                               # List containing cell agents
deltaT = 1                                  # time step for discretisation [T]
deltaR = 1                                  # space step for discretisation [L]  
deltaS = 0.5                                # decay rate for SGF 
deltaL = 0.1                                # decay rate for LGF
diffConst = 1.                              # diffusion constant D [dimentionless]
itime = 0                                   # time counter

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#       INITIALIZATION             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# create mother cell and update the grid with its initial location
cellList.append(cell(ix,iy))
cellGrid[ix][iy][0] = 1

# Plot figure and subplots
cellsFigure, cellsSubplot, sgfSubplot, lgfSubplot, cellPlot, sgfPlot, lgfPlot = Environment.CellsGridFigure(nLattice)

# DEBUG
print('Time running...')

while itime < timeSteps:
    # DEBUG 
    print('\ntime step #' + str(itime))
    
    for iPos in range(nLattice):
        for jPos in range(nLattice):
            if cellGrid[iPos,jPos][0] == -1:
                        cellGrid[iPos,jPos][1] = sgfDiffEq(cellGrid[iPos,jPos][1], 0, deltaS, deltaT)
#                        cellGrid[iPos,jPos][2] = lgfDiffEq(cellGrid[iPos,jPos][2], 0, deltaL, deltaT)
    
    tmpCellList = list(cellList)                                    # a copy of the list of current cells is used to iterate over all the cells
    while len(tmpCellList) > 0:                                     # while  the tmp list of cells is longer than 1
        # 1st step => choose a random cell from the list of existing cells
        rndCell = np.random.randint(len(tmpCellList))               
        
        # 2nd step => store lattice size
        tmpCellList[rndCell].border = nLattice                      # TODO rethink this                
        
        # 3rd step => read chemicals
        SGF_reading, LGF_reading = tmpCellList[rndCell].Sense(cellGrid)
        
        # 4th step => update SGF and LGF amounts on the grid
        cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)
        
        # 5th step => random cell should decide and action
        tmpCellList[rndCell].GenerateStatus(SGF_read, LGF_read)     # get status of this cell

        # DEBUG
        print('cell number: ' + str(len(cellList)) + '\nCell status: ' + str(tmpCellList[rndCell].state))# + '\n')
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #        Cell Action            #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#        
        # according to cell status perform action: split or stay quiet
        if tmpCellList[rndCell].state == 'Quiet':                   # Check the state
            tmpCellList[rndCell].Quiet(cellGrid)                    # call method that performs selected action
#            cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)            
#            tmpCellList[rndCell].sgfProduce(cellGrid)
            tmpCellList[rndCell].lgfProduce(cellGrid)
            del tmpCellList[rndCell]                                # delete cell from temporal list
         
        elif tmpCellList[rndCell].state == 'Split':
            tmpCellList[rndCell].Split2(cellGrid,cellList)
#            cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)
#            tmpCellList[rndCell].sgfProduce(cellGrid)
            tmpCellList[rndCell].lgfProduce(cellGrid)
            del tmpCellList[rndCell]

        elif tmpCellList[rndCell].state == 'Move':
            tmpCellList[rndCell].Move2(cellGrid)
#            cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)
            del tmpCellList[rndCell]
         
        else: # Die
            tmpCellList[rndCell].dieCounter += 1
            if tmpCellList[rndCell].dieCounter == tmpCellList[rndCell].dieTime:
                tmpCellList[rndCell].Die(cellGrid)                  # Off the grid, method also changes the "amidead" switch to True
#                cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, 0, deltaS, deltaT)
                del tmpCellList[rndCell]
#            else:
#                cellGrid[tmpCellList[rndCell].xPos,tmpCellList[rndCell].yPos][1] = sgfDiffEq(SGF_reading, tmpCellList[rndCell].sgfAmount, deltaS, deltaT)
        
        # after the cell reads the grid and performs an action the pheromone is updated according to the diff eq
        
    # while

    # A list of cells that "died" is stored to later actually kill the cells...
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
    #        Plot               #
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
    
    time.sleep(0.5)
    itime += 1
    
# while    

print(str(timeSteps)+' time steps complete')

# TODO look this up
#if __name__ == '__main__':
#    main()
