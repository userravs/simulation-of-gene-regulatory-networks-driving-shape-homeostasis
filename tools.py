import numpy as np
from scipy import linalg
import csv

#from scipy.sparse import diags

#class Tools:
#    def SortList(self, neighbours):
#        sortedNeighbours = list(neighbours)

# Tools
def CheckInBorders(xCoord, yCoord, border):
    if xCoord < 0 or xCoord > border:     # Check if the neighbour is inbounds on x axis
        return False
    elif yCoord < 0 or yCoord > border:    # Check if the neighbour is inbounds on y axis
        return False
    else:
        return True
# CheckInBorders
    
def CheckifOccupied(xCoord, yCoord, grid):
    if grid[xCoord, yCoord][0] > 0:         # if value on grid is 1 (quiet), 2 (moved) or 3 (splitted) then spot is occupied
        return True
    else:                                   # else, value is 0 (empty) or -1 (cell was there before but died) then spot is available
        return False
# CheckifOccupied

def CheckifPreferred(xOri, yOri, xCoord, yCoord):
    if xCoord == xOri and yCoord == yOri:
        return True
    else:
        return False
# CheckifPreferred

# SGF dynamics, single value update approach 
def sgfDiffEq(s, sigma, deltaS, deltaT):
    updatedVal = s + deltaT*(sigma - deltaS*s)
    return updatedVal
# sgfDiffEq

# SGF dynamics with matrix approach
def sgfDiffEq2(s_matrix, sigma_matrix, deltaS, deltaT):
    updated_matrix = s_matrix + deltaT*(sigma_matrix - deltaS*s_matrix)
    return updated_matrix
# sgfDiffEq

# TODO use linalg solve to make it fastes and more numerically stable
# LGF dynamics with matrix approach
def lgfDiffEq(i_matrix, t_matrix, l_matrix, lambda_matrix, deltaL, deltaT, deltaR, D):
    alpha = D*deltaT/(deltaR**2)                            # constant
    f = (deltaT/2.)*(lambda_matrix - deltaL*l_matrix)       # term that takes into account LFG production for half time step
    g = linalg.inv(i_matrix - (alpha/2.)*t_matrix)          # inverse of some intermediate matrix
    h = i_matrix + (alpha/2.)*t_matrix                      # some intermediate matrix
    l_halftStep = g@(l_matrix@h + f)                        # half time step calculation for LGF values
    #print('grid after half time step...\n' + str(l_halftStep))
    f = (deltaT/2.)*(lambda_matrix - deltaL*l_halftStep)    # updated term...
    l_tStep = (h@l_halftStep + f)@g                         # final computation
    return l_tStep
# sgfDiffEq

def lgfDiffEq2(i_matrix, t_matrix, l_matrix, lambda_matrix, deltaL, deltaT, deltaR, D):
    alpha = D*deltaT/(deltaR**2)                            # constant
    f = (deltaT/2.)*(lambda_matrix - deltaL*l_matrix)       # term that takes into account LFG production for half time step
    g = linalg.inv(i_matrix - (alpha/2.)*t_matrix)          # inverse of some intermediate matrix
    h = i_matrix + (alpha/2.)*t_matrix                      # some intermediate matrix
    l_halftStep = (l_matrix@h + f)@g                        # half time step calculation for LGF values
    f = (deltaT/2.)*(lambda_matrix - deltaL*l_halftStep)    # updated term...
    l_tStep = g@(h@l_halftStep + f)                         # final computation
    return l_tStep
# sgfDiffEq

# T matrix, used in LGF dynamics
def GenerateTMatrix(size):
    t_matrix = np.zeros([size,size])
    for ix in range(size - 1):
        t_matrix[ix,ix] = -2.
        t_matrix[ix,ix + 1] = 1.
        t_matrix[ix + 1,ix] = 1.
    t_matrix[0,0] = -1.
    t_matrix[size - 1, size - 1] = -1.
    return t_matrix        
# GenerateTMatrix

# Identity matrix
def GenerateIMatrix(size):
    I_matrix = np.zeros([size,size])
    for ix in range(size):
        I_matrix[ix,ix] = 1.
    return I_matrix
# GenerateIMatrix

#def diffusion_FTCS(deltaT, deltaS, t_max, y_max, const, init_cond):
    ## diffusion number (has to be less than 0.5 for the 
    ## solution to be stable):
    #alpha = const*deltaT/(deltaS**2)
    #y = np.arange(0, y_max + dy, dy) 
    #t = np.arange(0, t_max + dt, dt)
    #r = len(t)
    #c = len(y)
    #V = np.zeros([r,c])
    #V[:,0] = V0
    #for n in range(0,r - 1):            # time
        #for j in range(1,c - 1):        # space
            #V[n + 1,j] = V[n,j] + s*(V[n,j - 1] - 2*V[n,j] + V[n,j + 1]) 
    #return y,V,r,s
## diffusion_FTCS

#def diffusion_Laasonen(dt,dy,t_max,y_max,viscosity,V0,V1):
    #s = viscosity*dt/dy**2              # diffusion number
    #y = np.arange(0,y_max+dy,dy) 
    #t = np.arange(0,t_max+dt,dt)
    #nt = len(t)                         # number of time steps
    #ny = len(y)                         # number of dy steps
    #V = np.zeros((ny,))                 # initial condition
    #V[0] = V0                           # boundary condition on left side
    #V[-1] = V1                          # boundary condition on right side
    ## create coefficient matrix:
    #A = diags([-s, 1+2*s, -s], [-1, 0, 1], shape=(ny-2, ny-2)).toarray() 
    #for n in range(nt):                 # time is going from second time step to last
        #Vn = V                          #.copy()
        #B = Vn[1:-1]                    # create matrix of knowns on the RHS of the equation
        #B[0] = B[0]+s*V0
        #B[-1] = B[-1]+s*V1
        #V[1:-1] = np.linalg.solve(A,B)  # solve the equation using numpy
    #return y,t,V,s
# diffusion_Laasonen

def NeuralNetwork(inputs, WMatrix, wMatrix, phi, theta):
    #nNodes = 10  # number of nodes
    V = np.zeros([6])
    O = np.zeros([6])
    bj = wMatrix@inputs - theta
    for ix in range(len(bj)):
        V[ix] = TransferFunction(bj[ix],2)
    
    bi = WMatrix@V - phi
    for ix in range(len(bi)):
        O[ix] = TransferFunction(bi[ix],2)
    return O
# NeuralNetwork

def TransferFunction(x,beta):
    return 1./(1 + np.exp(-beta*x))
# TransferFunction

def RecurrentNeuralNetwork(inputs, wMatrix, V):
    #nNodes = 10  # number of nodes
    bj = wMatrix@V - inputs
    for ix in range(len(bj)):
        V[ix] = TransferFunction(bj[ix],2)
    return V
# NeuralNetwork

def GetStructure(cell_array, nLattice):
    structure = np.zeros([nLattice,nLattice])
    for ik in range(nLattice):
        for jk in range(nLattice):
            if cell_array[ik,jk] != 0:
                structure[ik,jk] = 1
    return structure
# GetStructure

def GetrNN():
    with open('test_file.csv', 'r') as csvfile:
        #reader = csv.reader(csvfile)
        wMatrix = np.loadtxt(csvfile,delimiter=',')
    return wMatrix
