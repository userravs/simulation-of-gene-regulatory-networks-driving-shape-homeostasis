import time
import random 
import numpy as np
import matplotlib.pyplot as plt
from cell_agent import Cell		# it is allowed to call from this class because there's an __init__.py file in this directory

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#	PARAMETERS			#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
nLattice = 128 # Lattice Size
timeSteps = 1000 # Number of simulation time steps
p = 0.5 # Probability of splitting for any time step
# f = 1 # Lightning probability.
cellGrid = np.zeros([nLattice+2,nLattice+2]) # Initialize empty forest
SGF_read = 0	# in the future values will be read from the grid
LGF_read = 0

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#	INITIALIZATION			#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
fig = plt.figure()

# initialise mother cell
mother_cell = cell(nLattice/2,nLattice/2)
cellList = [[mother_cell.xPos,mother_cell.yPos]]
time = 0
print('Time running...')

while time < timeSteps:
##    print('time step #'+str(time))
    #forestLattice = UpdateForest(forestLattice,nLattice,p)
    #time += 1
    #ignitedTrees = []
    #fireAlert = 0 # turn off the fire alert
    
    ## A random lightning strike initiates a fire
    #r = np.random.random()
    #if r < f:
        #rXPos = random.randint(1,nLattice)
        #rYPos = random.randint(1,nLattice)
        #if forestLattice[rYPos,rXPos] == 1:
            #forestLattice[rYPos,rXPos] = -1
            #ignitedTrees.append([rYPos,rXPos])
            #fireCounter += 1 # variable n
            #fireAlert = 1 # there's a fire in this timestep
    
    ## if there's a fire in this time step...                
    #if fireAlert == 1: 
        #forestLattice = FireSpread(forestLattice,ignitedTrees)
##        burnedTrees = len(ignitedTrees)
##        treeDensity.append(burnedTrees/(nLattice**2))

	tmpCellList = list(cellList)		# a copy of the list of current cells is used to iterate over all the cells
	while len(tmpCellList) > 0:				# while  the tmp list of cells is longer than 1
		rndCell = np.random.randint(len(tmpCellList))
		# random cell should decide and action
		
# first update cell status
    status = GenerateStatus(SGF_read, LGF_read)

# according to cell status perform action: split or stay quiet
	if(status == 1):
		newGrid = Split(cellGrid)

# plot grid

# repeat
    

## IMSHOW PLOT, must be in the fire spread while            
    plt.clf()
    plt.imshow(cellGrid, origin='lower', cmap='RdYlGn', interpolation='none', vmin =-1, vmax = 1)
    plt.colorbar()
    fig.canvas.draw()
    time.sleep(0.51) 
#    plt.savefig('fire_spread-p'+str(p)+'-f'+str(f)+'-timeStep'+str(time)+'.png', bbox_inches='tight')



print(str(timeSteps)+' time steps complete')
