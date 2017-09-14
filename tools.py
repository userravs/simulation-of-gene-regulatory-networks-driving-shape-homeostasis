import numpy as np
import matplotlib.pyplot as plt

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
    if grid[xCoord, yCoord][0] == 1:
        return True
    else:
        return False
# CheckifOccupied

def CheckifPreferred(xOri, yOri, xCoord, yCoord):
    if xCoord == xOri and yCoord == xOri:
        return True
    else:
        return False
# CheckifPreferred
