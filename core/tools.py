import numpy as np
from scipy import linalg
import csv
from numba import jit

# Tools
#@jit
#def CheckInBorders(xCoord, yCoord, border):
    #if xCoord < 0 or xCoord > border:     # Check if the neighbour is inbounds on x axis
        #return False
    #elif yCoord < 0 or yCoord > border:    # Check if the neighbour is inbounds on y axis
        #return False
    #else:
        #return True
# CheckInBorders

# List without joint ends
# https://stackoverflow.com/questions/29710249/python-force-list-index-out-of-range-exception
class flatList(list):
    """
    A list subclass that raises IndexError for negative indices.
    
    This prevents circular indexing behavior that could cause issues
    in the cellular automata grid operations.
    """
    def __getitem__(self, index):
        if index < 0:
            raise IndexError("list index out of range")
        return super(flatList, self).__getitem__(index)

#@jit
def CheckifOccupied(xCoord, yCoord, grid):
    """
    Check if a grid position is occupied by a cell.
    
    Parameters:
    -----------
    xCoord, yCoord : int
        Grid coordinates to check
    grid : numpy.ndarray
        2D grid array where values > 0 indicate occupied positions
    
    Returns:
    --------
    bool
        True if position is occupied, False otherwise
    """
    if grid[yCoord][xCoord] > 0:         # if value on grid is 1 (quiet), 2 (moved) or 3 (splitted) then spot is occupied
        return True
    else:                                   # else, value is 0 (empty) or -1 (cell was there before but died) then spot is available
        return False
# CheckifOccupied

#@jit
def CheckifPreferred(xOri, yOri, xCoord, yCoord):
    """
    Check if a position matches the preferred orientation direction.
    
    Parameters:
    -----------
    xOri, yOri : int
        Preferred orientation coordinates
    xCoord, yCoord : int
        Position coordinates to check
    
    Returns:
    --------
    bool
        True if position matches preferred direction, False otherwise
    """
    if xCoord == xOri and yCoord == yOri:
        return True
    else:
        return False
# CheckifPreferred

# SGF dynamics, single value update approach
#@jit
#def SGFDiffEq(s, sigma, deltaS, deltaT):
    #updatedVal = s + deltaT*(sigma - deltaS*s)
    #return updatedVal
# sgfDiffEq

# SGF dynamics with matrix approach
# @jit # WARNING ON is good! - temporarily disabled for testing
def SGFDiffEq(s_matrix, sigma_matrix, deltaS, deltaT):
    """
    Update SGF (Short-range Growth Factor) concentrations using matrix operations.
    
    Implements the diffusion equation for SGF: ds/dt = σ - δs
    where σ is production rate and δ is decay rate.
    
    Parameters:
    -----------
    s_matrix : numpy.ndarray
        Current SGF concentration matrix
    sigma_matrix : numpy.ndarray
        SGF production matrix
    deltaS : float
        SGF decay rate
    deltaT : float
        Time step size
    
    Returns:
    --------
    numpy.ndarray
        Updated SGF concentration matrix
    """
    updated_matrix = s_matrix + deltaT*(sigma_matrix - deltaS*s_matrix)
    return updated_matrix
# sgfDiffEq

# TODO use linalg solve to make it faster and numerically more stable
# LGF dynamics with matrix approach
# @jit # WARNING ON is good! - temporarily disabled for testing
def LGFDiffEq(i_matrix, t_matrix, l_matrix, lambda_matrix, deltaL, deltaT, deltaR, D):
    """
    Update LGF (Long-range Growth Factor) concentrations using matrix operations.
    
    Implements the diffusion equation for LGF with spatial diffusion:
    dl/dt = D∇²l + λ - δl
    where D is diffusion constant, λ is production rate, and δ is decay rate.
    
    Uses a semi-implicit Crank-Nicolson scheme for numerical stability.
    
    Parameters:
    -----------
    i_matrix : numpy.ndarray
        Identity matrix
    t_matrix : numpy.ndarray
        T-matrix for spatial discretization
    l_matrix : numpy.ndarray
        Current LGF concentration matrix
    lambda_matrix : numpy.ndarray
        LGF production matrix
    deltaL : float
        LGF decay rate
    deltaT : float
        Time step size
    deltaR : float
        Spatial step size
    D : float
        Diffusion constant
    
    Returns:
    --------
    numpy.ndarray
        Updated LGF concentration matrix
    """
    alpha = D*deltaT/(deltaR**2)                            # constant
    f = (deltaT/2.)*(lambda_matrix - deltaL*l_matrix)       # term that takes into account LFG production for half time step
    g = linalg.inv(i_matrix - (alpha/2.)*t_matrix)          # inverse of some intermediate matrix
    h = i_matrix + (alpha/2.)*t_matrix                      # some intermediate matrix
    l_halftStep = g@(l_matrix@h + f)                        # half time step calculation for LGF values
    #l_halftStep = np.matmul(g,(np.matmul(l_matrix,h) + f))                        # half time step calculation for LGF values
    #print('grid after half time step...\n' + str(l_halftStep))
    f = (deltaT/2.)*(lambda_matrix - deltaL*l_halftStep)    # updated term...
    l_tStep = ((h@l_halftStep) + f)@g
    # l_tStep = np.matmul((np.matmul(h,l_halftStep) + f),g)                         # final computation
    return l_tStep
# sgfDiffEq

#def LGFDiffEq2(i_matrix, t_matrix, l_matrix, lambda_matrix, deltaL, deltaT, deltaR, D):
    #alpha = D*deltaT/(deltaR**2)                            # constant
    #f = (deltaT/2.)*(lambda_matrix - deltaL*l_matrix)       # term that takes into account LFG production for half time step
    #g = linalg.inv(i_matrix - (alpha/2.)*t_matrix)          # inverse of some intermediate matrix
    #h = i_matrix + (alpha/2.)*t_matrix                      # some intermediate matrix
    #l_halftStep = (l_matrix@h + f)@g                        # half time step calculation for LGF values
    #f = (deltaT/2.)*(lambda_matrix - deltaL*l_halftStep)    # updated term...
    #l_tStep = g@(h@l_halftStep + f)                         # final computation
    #return l_tStep
# sgfDiffEq

# T matrix, used in LGF dynamics
#@jit
def GenerateTMatrix(size):
    """
    Generate the T-matrix for spatial discretization in LGF diffusion.
    
    The T-matrix represents the discrete Laplacian operator for finite differences.
    
    Parameters:
    -----------
    size : int
        Size of the square matrix to generate
    
    Returns:
    --------
    numpy.ndarray
        T-matrix for LGF diffusion calculations
    """
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
#@jit
def GenerateIMatrix(size):
    """
    Generate an identity matrix of specified size.
    
    Parameters:
    -----------
    size : int
        Size of the square matrix to generate
    
    Returns:
    --------
    numpy.ndarray
        Identity matrix of size x size
    """
    I_matrix = np.zeros([size,size])
    for ix in range(size):
        I_matrix[ix,ix] = 1.
    return I_matrix
# GenerateIMatrix

#def NeuralNetwork(inputs, WMatrix, wMatrix, phi, theta):
    ##nNodes = 10  # number of nodes
    #V = np.zeros([6])
    #O = np.zeros([6])
    #bj = wMatrix@inputs - theta
    #for ix in range(len(bj)):
        #V[ix] = TransferFunction(bj[ix],2)

    #bi = WMatrix@V - phi
    #for ix in range(len(bi)):
        #O[ix] = TransferFunction(bi[ix],2)
    #return O
# NeuralNetwork

#@jit
#def TransferFunction(x,beta):
    #return 1./(1 + np.exp(-beta*x))
## TransferFunction

# @jit #WARNING ON is good! - temporarily disabled for testing
def RecurrentNeuralNetwork(inputs, wMatrix, V):             # Recurrent Neural Network dynamics
    #beta = 2
    # bj = wMatrix@V - inputs
    bj = wMatrix @ V - inputs
    # might be improved ussing list comprehension...
    for ix in range(len(bj)):
        V[ix] = 1./(1 + np.exp(-2*bj[ix]))   #TransferFunction(bj[ix],2)
    # V = [1./(1 + np.exp(-2*bj[ix])) for ix in range(len(bj))]
    return V
# NeuralNetwork

#@jit
def GetStructure(cell_array, nLattice):
    structure = np.zeros([nLattice,nLattice])
    for ik in range(nLattice):
        for jk in range(nLattice):
            if cell_array[ik,jk] != 0:
                structure[ik,jk] = 1
    return structure
# GetStructure

def GetrNN(csvFile, ind):
    #with open('successful_test.csv', 'r') as csvfile:
    with open(csvFile, 'r') as csvfile:
        #reader = csv.reader(csvfile)
        bestIndividuals = np.loadtxt(csvfile,delimiter=',')
    # get nNodes from nGenes
    nNodes = int(np.sqrt(len(bestIndividuals[ind,:])))
    wMatrix = np.array(bestIndividuals[ind,:].reshape(nNodes,nNodes))
    return wMatrix
