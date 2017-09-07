import time
import random 
import numpy as np
import matplotlib.pyplot as plt
from cell_agent import *	# it is allowed to call from this class because there's an __init__.py file in this directory

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#	PARAMETERS			#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
nLattice = 20 # Lattice Size
timeSteps = 15 # Number of simulation time steps
p = 0.5 # Probability of splitting for any time step
# f = 1 # Lightning probability.
cellGrid = np.zeros([nLattice,nLattice]) # Initialize empty forest
SGF_read = 0	# in the future values will be read from the grid
LGF_read = 0

ix = int(nLattice/2)
iy = int(nLattice/2)

#def main():

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#	INITIALIZATION			#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
plt.ion()
fig = plt.figure()

# initialise mother cell
#mother_cell = cell(nLattice/2,nLattice/2)
#cellList = [[mother_cell.xPos,mother_cell.yPos]]
cellList = []

# create mother cell and update the grid with its initial location
cellList.append(cell(ix,iy))
cellGrid[ix][iy] = 1

im = plt.imshow(cellGrid, origin='lower', cmap='RdYlGn', interpolation='none', vmin =-1, vmax = 1)
plt.colorbar()
plt.show()
#plt.draw()

itime = 0
print('Time running...')

while itime < timeSteps:
	print('time step #'+str(itime))
    
	tmpCellList = list(cellList)		# a copy of the list of current cells is used to iterate over all the cells
	
	while len(tmpCellList) > 0:		# while  the tmp list of cells is longer than 1
		rndCell = np.random.randint(len(tmpCellList)) # choose a random cell in the list of existing cells
		# random cell should decide and action
		# first update cell status
		status = tmpCellList[rndCell].GenerateStatus(SGF_read, LGF_read)	# get status of this cell
		# according to cell status perform action: split or stay quiet
		if status == 1:		# Split
			tmpCellList[rndCell].Split(cellGrid,cellList)
			del tmpCellList[rndCell]
		elif status == 2 	# Move
		else:	# Die
		
	# while
	
## IMSHOW PLOT, must be in the fire spread while            

#	plt.close()	
#	ax = fig.add_subplot(111)
#	#fig.suptitle('')
##	ax.set_xlabel('Relative fire size')
##	ax.set_ylabel('cCDF')
##	ax.set_xscale('log')
##	ax.set_yscale('log')
#	ax.set_title('Rank-frequency plot')   
#	ax.imshow(cellGrid, origin='lower', cmap='RdYlGn', interpolation='none', vmin =-1, vmax = 1)
#	ax.legend(loc='best')
##	plt.savefig('ex2.3.png')
#	fig.canvas.draw()
#	time.sleep(0.5) 

	plt.clf()
	im = plt.imshow(cellGrid, origin='lower', cmap='RdYlGn', interpolation='none', vmin =-1, vmax = 1)
#	im.set_data(cellGrid)
#	plt.colorbar()
	fig.canvas.update()
	fig.canvas.flush_events()
#	plt.draw()
#	plt.show()
#	time.sleep(0.75) 

##	plt.savefig('fire_spread-p'+str(p)+'-f'+str(f)+'-timeStep'+str(time)+'.png', bbox_inches='tight')
	itime +=1
# while	

plt.ioff()

print(str(timeSteps)+' time steps complete')

#if __name__ == '__main__':
#	main()
