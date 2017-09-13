#from PyQt4 import QtGui, QtCore
import time
import random 
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib
from cell_agent import *    # it is allowed to call from this class because there's an __init__.py file in this directory
from tools import *


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#    	Functions                  #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#def CheckifOccupied(xCoord, yCoord, grid):
#    if grid[xCoord, yCoord][0] == 1:
#        return True
#    else:
#        return False

#def CheckInBorders(xCoord, yCoord, border):
#    if xCoord >= 0 and xCoord <= border:     # Check if the neighbour is inbounds on x axis
#        return False
#    elif yCoord >= 0 and yCoord <= border:    # Check if the neighbour is inbounds on y axis
#        return False
#    else:
#        return True
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#    	PARAMETERS                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
nLattice = 100 					# Lattice Size
timeSteps = 80 					# Number of simulation time steps
cellGrid = np.zeros([nLattice,nLattice,3]) 	# Initialize empty grid
SGF_read = 0    				# in the future values will be read from the grid
LGF_read = 0
ix = int(nLattice/2)				# Initial position for the mother cell
iy = int(nLattice/2)
cellList = []

# create mother cell and update the grid with its initial location
cellList.append(cell(ix,iy))
cellGrid[ix][iy][0] = 1
agentsGrid = cellGrid[:,:,0] 		# slice the grid to get the layer with the cell positions
sgfGrid = cellGrid[:,:,1] 		# slice the grid to get the layer with the cell positions
lgfGrid = cellGrid[:,:,2] 		# slice the grid to get the layer with the cell positions

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#    	INITIALIZATION             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

plt.ion()
#if matplotlib.is_interactive():
#	pylab.ioff()
fig = plt.figure()

### NEW PLOTTING CODE
ax = fig.add_subplot(131)
ay = fig.add_subplot(132)
az = fig.add_subplot(133)
fig.suptitle('Cell system')
ax.set_title('Cells') 
ay.set_title('LGF') 
az.set_title('SGF') 

ax.imshow(agentsGrid, origin='lower', cmap='PuOr', interpolation='none', vmin = -1, vmax = 1)
ay.imshow(sgfGrid, origin='lower', cmap='binary', interpolation='none', vmin = 0, vmax = 10)
az.imshow(lgfGrid, origin='lower', cmap='binary', interpolation='none', vmin = 0, vmax = 10)
#ax.legend(loc='best')
fig.canvas.draw()

### END PLOTTING CODE


### OLD PLOTTING CODE
##plt.ioff()
#plt.gcf().show()
#im = plt.imshow(agentsGrid, origin='lower', cmap='PuOr', interpolation='none', vmin =-1, vmax = 1)
##im.set_data(agentsGrid)
#plt.colorbar()
#plt.show()
##plt.draw()
### END OF OLD PLOTTING CODE

itime = 0

# DEBUG
print('Time running...')

while itime < timeSteps:
    # DEBUG 
    print('\ntime step #' + str(itime))
    
    tmpCellList = list(cellList)				# a copy of the list of current cells is used to iterate over all the cells
    
    while len(tmpCellList) > 0:					# while  the tmp list of cells is longer than 1
        rndCell = np.random.randint(len(tmpCellList))	 	# choose a random cell in the list of existing cells
        # random cell should decide and action
        tmpCellList[rndCell].border = nLattice
        
        # first update cell status
        tmpCellList[rndCell].GenerateStatus(SGF_read, LGF_read)	# get status of this cell

        # DEBUG
        print('cell number: ' + str(len(cellList)) + '\nCell status: ' + str(tmpCellList[rndCell].state))# + '\n')
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #        Cell Action                #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#        
        # according to cell status perform action: split or stay quiet
        if tmpCellList[rndCell].state == 'Quiet':		# Check the state
            tmpCellList[rndCell].Quiet()			# call method that performs selected action
            del tmpCellList[rndCell]				# delete cell from temporal list
         
        elif tmpCellList[rndCell].state == 'Split':
            tmpCellList[rndCell].Split(cellGrid,cellList)
            del tmpCellList[rndCell]

        elif tmpCellList[rndCell].state == 'Move':
            tmpCellList[rndCell].Move(cellGrid)
            del tmpCellList[rndCell]
         
	# WARNING see TODO
        else: # Die
            tmpCellList[rndCell].Die(cellGrid)			# Off the grid
            del tmpCellList[rndCell]
            # TODO this way of killing the cell doesn't work, cellList and tmpCellList not necesarily have the same length 
            del cellList[rndCell] 				# Actual death                

    ### TEST! equivalent to: cellList[cell].'status'(param_x,param_y)
    #    state = getattr(tmpCellList[rndCell], status)
    #    action = getattr(tmpCellList[rndCell], state)
    #    action(cellGrid, cellList)
    # while
    
    ## IMSHOW PLOT, must be in the fire spread while            

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #        Plot                #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~#

### NEW CODE
    plt.clf()
    ax.imshow(agentsGrid, origin='lower', cmap='PuOr', interpolation='none', vmin = -1, vmax = 1)
    ay.imshow(sgfGrid, origin='lower', cmap='binary', interpolation='none', vmin = 0, vmax = 10)
    az.imshow(lgfGrid, origin='lower', cmap='binary', interpolation='none', vmin = 0, vmax = 10)
    fig.canvas.update()
    fig.canvas.flush_events()
    #fig.canvas.draw()
    #time.sleep(0.5) 

### NEW CODE

### OLD CODE

#    plt.clf()
#    im = plt.imshow(agentsGrid, origin='lower', cmap='PuOr', interpolation='none', vmin =-1, vmax = 1)
#    #im.set_data(agentsGrid)
#    plt.colorbar()
#    #im.set_visible(False)
#    #plt.ion()
#    fig.canvas.update()
#    fig.canvas.flush_events()
#    #plt.ioff()
#    #im.draw_artist(cellGrid)
#    #plt.show()
#    #time.sleep(0.75) 
#    #plt.savefig('fire_spread-p'+str(p)+'-f'+str(f)+'-timeStep'+str(time)+'.png', bbox_inches='tight')

### OLD CODE

    itime += 1

# while    

plt.ioff()

print(str(timeSteps)+' time steps complete')

#if __name__ == '__main__':
#    main()
