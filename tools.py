import numpy as np
from scipy.sparse import diags

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
    if grid[xCoord, yCoord][0] != 0:
        return True
    else:
        return False
# CheckifOccupied

def CheckifPreferred(xOri, yOri, xCoord, yCoord):
    if xCoord == xOri and yCoord == yOri:
        return True
    else:
        return False
# CheckifPreferred

def sgfDiffEq(s, sigma, deltaS, deltaT):
    return s + deltaT*(-deltaS*s + sigma)
# sgfDiffEq

#def lgfDiffEq(l, lambda, deltaL, deltaT, D):
#    return l + deltaT*(-deltaL*l + lambda)
# sgfDiffEq

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
