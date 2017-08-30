#import sys
import time
import random 
import numpy as np
import matplotlib.pyplot as plt

#######################################################
######### PARAMETERS

nLattice = 128 # Lattice Size
timeSteps = 1000 # Number of simulation time steps
p = 0.04 # Probability of growing a tree on an empty site
f = 1 # Lightning probability.
forestLattice = np.zeros([nLattice+2,nLattice+2]) # Initialize empty forest

#######################################################
######### FUNCTIONS
# Function that updates periodic boundaries of the forest
def UpdatePeriodicBoundary(oldLattice,nLattice):
    updatedLattice = np.array(oldLattice)
    updatedLattice[nLattice+1,:] = oldLattice[1,:]
    updatedLattice[0,:] = oldLattice[nLattice,:]
    updatedLattice[:,nLattice+1] = oldLattice[:,1]
    updatedLattice[:,0] = oldLattice[:,nLattice]
    return updatedLattice

# Function that randomly grows trees in random positions
def UpdateForest(forestLattice,nLattice,p):
    for xPos in range(1,nLattice+1):
        for yPos in range(1,nLattice+1):
            if forestLattice[xPos][yPos] <= 0:
                r = np.random.random()
                if r < p:
                    forestLattice[xPos][yPos] = 1 # Grow a tree
                else:
                    forestLattice[xPos][yPos] = 0
    forestLattice = UpdatePeriodicBoundary(forestLattice,nLattice)
    return forestLattice

# Get tree density before a fire
def GetTreeDensity(forestLattice,nLattice):
    treeDensity = 0
    for xPos in range(1,nLattice+1):
        for yPos in range(1,nLattice+1):
            if forestLattice[xPos][yPos] == 1:
                treeDensity +=1
    return treeDensity/nLattice**2

# Generate a random forest with a given density
def RandomForest(nLattice,forestDensity,p):
    treeCounter = 0
    newForestDensity = 0
    randomForestLattice = np.zeros([nLattice+2,nLattice+2])
    while newForestDensity < forestDensity:
        for xPos in range(1,nLattice+1):
            for yPos in range(1,nLattice+1):
                r = np.random.random()
                if r < p:
                    randomForestLattice[xPos][yPos] = 1 # Grow a tree
                    treeCounter += 1
        newForestDensity = treeCounter/nLattice**2
    return randomForestLattice

# function that returns a random position with a tree to burn
def randomTreePos(nLattice,randomWoods):
    alarm = 0
    while alarm == 0:
        rXPos = random.randint(1,nLattice)
        rYPos = random.randint(1,nLattice)
        if randomWoods[rXPos,rYPos] == 1:  
            randomWoods[rXPos,rYPos] = -1      
            alarm = 1
    ignitedRndForestTrees = [[rXPos,rYPos]]
    return ignitedRndForestTrees

# Linear function
def LinearFunc(x,m,b):
    return (x**m)*(10**b)

# Function that spread the fire in a cluster of trees
def FireSpread(forestLattice,ignitedTrees):
    fire = 0
    # Spread the fire
    while fire < len(ignitedTrees):
        fireXPos = ignitedTrees[fire][1]
        fireYPos = ignitedTrees[fire][0]         

        # Set neighbors positions
        # Set up neighbor
        if fireYPos == 1:
            upNYP = nLattice
        else:
            upNYP = fireYPos-1
        
        # Set down neighbor
        if fireYPos == nLattice:
            downNYP = 1
        else:
            downNYP = fireYPos+1
        
        # Set left neighbor
        if fireXPos == 1:
            leftNXP = nLattice
        else:
            leftNXP = fireXPos-1
        
        # Set right neighbor
        if fireXPos == nLattice:
            rightNXP = 1
        else:
            rightNXP = fireXPos+1
        
        # Check neighbors state, if there's a tree, spread the fire
        if forestLattice[upNYP,fireXPos] == 1:
            forestLattice[upNYP,fireXPos] = -1
            ignitedTrees.append([upNYP,fireXPos])
        if forestLattice[downNYP,fireXPos] == 1:
            forestLattice[downNYP,fireXPos] = -1
            ignitedTrees.append([downNYP,fireXPos])
        if forestLattice[fireYPos,rightNXP] == 1:
            forestLattice[fireYPos,rightNXP] = -1
            ignitedTrees.append([fireYPos,rightNXP])
        if forestLattice[fireYPos,leftNXP] == 1:
            forestLattice[fireYPos,leftNXP] = -1
            ignitedTrees.append([fireYPos,leftNXP])
              
        fire += 1
    return forestLattice

#---------------------------------------------------------
#######################################################
# PROGRAM INITIALIZATION
#######################################################
fig = plt.figure()

treeDensity = []
tStep = 0
fireCounter = 0
print('Time running...')
while tStep < timeSteps:
#    print('time step #'+str(tStep))
    forestLattice = UpdateForest(forestLattice,nLattice,p)
    tStep += 1
    ignitedTrees = []
    fireAlert = 0 # turn off the fire alert
    
    # A random lightning strike initiates a fire
    r = np.random.random()
    if r < f:
        rXPos = random.randint(1,nLattice)
        rYPos = random.randint(1,nLattice)
        if forestLattice[rYPos,rXPos] == 1:
            forestLattice[rYPos,rXPos] = -1
            ignitedTrees.append([rYPos,rXPos])
            fireCounter += 1 # variable n
            fireAlert = 1 # there's a fire in this timestep
    
    # if there's a fire in this time step...                
    if fireAlert == 1: 
        forestLattice = FireSpread(forestLattice,ignitedTrees)
#        burnedTrees = len(ignitedTrees)
#        treeDensity.append(burnedTrees/(nLattice**2))

## IMSHOW PLOT, must be in the fire spread while            
    plt.clf()
    plt.imshow(forestLattice, origin='lower', cmap='RdYlGn', interpolation='none', vmin =-1, vmax = 1)
    plt.colorbar()
    fig.canvas.draw()
#    time.sleep(0.51) 
    plt.savefig('fire_spread-p'+str(p)+'-f'+str(f)+'-timeStep'+str(tStep)+'.png', bbox_inches='tight')

print(str(timeSteps)+' time steps complete')