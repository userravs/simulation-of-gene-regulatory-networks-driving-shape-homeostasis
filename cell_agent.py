import numpy as np
import matplotlib.pyplot as plt
from tools import *

class cell:
    # defines whats needed when a new agent (Cell) of this class is created
    def __init__(self, xPos, yPos):
        self.xPos = xPos                            # Initial position on x axis
        self.yPos = yPos                            # Initial position on y axis
        self.splitCounter = 0                       # Counter for splitting
        self.splitTime = 2                          # Time scale for splitting
        self.dieCounter = 0                         # Counter for dying
        self.dieTime = 3                            # Time scale for dying
        self.amidead = False                        # Cell dead or alive
        self.quietCounter = 0                       # Quiet counter
        self.orientation = [self.xPos,self.yPos]    # Preferred direction. DEFAULT: own position
        self.compass = True                         # Polarisation: ON/OFF
        self.state = 'Quiet'                        # State of the cell. DEFAULT: quiet
        self.border = 0                             # size of the lattice
        self.sgfAmount = 0                          # Amount of "pheromone" to deposit in the grid
        self.lgfAmount = 0
    # self
    
    #   Values stored in grid according to state:
    #       -1  =>  a cell was there before but died or moved away
    #       0   =>  spot has been always empty i.e. available
    #       1   =>  quiet cell
    #       2   =>  moving cell
    #       3   =>  divided cell

    #def Get Pos(self):
        #return

    # WARNING Do I use this method??
    #def GetNeighbours(self, grid, border):
        #neighbourList = []
        ## TODO check if this works if orientation is OFF
        ## if orientation is OFF the method returns the probable neighbours
        #if self.xPos - 1 >= 0: # if coordinate is in-bounds
            #if grid[self.xPos - 1, self.yPos][0] == 0 and self.orientation[0] != self.xPos - 1 and self.orientation[1] != self.yPos:
                ## if is not occupied and not the preferred neighbour
                #neighbourList.append([self.xPos - 1, self.yPos]) 
        #if self.xPos + 1 <= border:
            #if grid[self.xPos + 1, self.yPos][0] == 0 and self.orientation[0] != self.xPos + 1 and self.orientation[1] != self.yPos:
                #neighbourList.append([self.xPos + 1, self.yPos])
        #if self.yPos - 1 >= 0:
            #if grid[self.xPos, self.yPos - 1][0] == 0 and self.orientation[0] != self.xPos and self.orientation[1] != self.yPos - 1:
                #neighbourList.append([self.xPos, self.yPos - 1])
        #if self.yPos + 1 <= border:
            #if grid[self.xPos, self.yPos + 1][0] == 0 and self.orientation[0] != self.xPos and self.orientation[1] != self.yPos + 1:
                #neighbourList.append([self.xPos, self.yPos + 1])
        ## returns a list of possible neighbours which are not the prefered
        #return neighbourList

    def Sense(self, grid):
        # sense chemicals from the grid
        SGF_reading = grid[self.xPos, self.yPos][1] # grid contains three values on each coordinate: 
        LGF_reading = grid[self.xPos, self.yPos][2] # occupation (boolean), SGF level, LGF level
        #reads = [SGF_read, LGF_read]
        return SGF_reading, LGF_reading
    # Sense   

    def sgfProduce(self, grid):
        grid[self.xPos, self.yPos][1] += self.sgfAmount
    # sgfProduce

    def lgfProduce(self, grid):
        grid[self.xPos, self.yPos][2] += self.lgfAmount
    # lgfProduce

    def GenerateStatus(self, SGF_read, LGF_read):
        # neural network generates a status based on the reads
        border = self.border
        # possible states: split, move, die
        iStatus = np.random.random()        # Proliferate:  Split
        jStatus = np.random.random()        # Move:         Move
        kStatus = np.random.random()        # Apoptosis:    Die
        # values for SGF and LGF
        self.sgfAmount = np.random.randint(5)
        self.lgfAmount = np.random.randint(5)

        # ORIENTATION:
        # randomly sets a preferred neighbour (polarisation)
        # if the direction is out of bounds then no preferred direction is stored 
        # WARNING This code need to be revisited depending on the implementation of the NN later on
        if self.compass:
            # boundaries for orientation
            nBoundary = 0.15
            #sBoundary = 0.5
            #eBoundary = 0.75
            #wBoundary = 1
            arrow = np.random.random()
            if arrow < nBoundary:
                xCoord = self.xPos - 1
                yCoord = self.yPos
                # orientation North
                if CheckInBorders(xCoord, yCoord, border):
                    self.orientation = [xCoord, yCoord]
            #elif arrow < sBoundary:
                ## orientation South
                #xCoord = self.xPos + 1
                #yCoord = self.yPos
                ## orientation North
                #if CheckInBorders(xCoord, yCoord, border):
                    #self.orientation = [xCoord, yCoord]
            #elif arrow < eBoundary:
                ## orientation East
                #xCoord = self.xPos
                #yCoord = self.yPos + 1
                ## orientation North
                #if CheckInBorders(xCoord, yCoord, border):
                    #self.orientation = [xCoord, yCoord]
            else:   #arrow < wBoundary:
                # orientation West
                xCoord = self.xPos
                yCoord = self.yPos - 1
                # orientation North
                if CheckInBorders(xCoord, yCoord, border):
                    self.orientation = [xCoord, yCoord]
        # if

        # Generate state
        maxVal = 0.5
        #tmpVal = 0
        xThreshold = 0.5
        yThreshold = 0.01
        
        if iStatus < xThreshold and jStatus < xThreshold and kStatus < xThreshold:
            self.state = 'Quiet'
            # DEBUG
            print('split = ' + str(iStatus) + ', move = ' + str(jStatus) + '\ndie = ' + str(kStatus) + '. Max: quiet\n')

        else:
            for ix in iStatus, jStatus, kStatus:
                if maxVal < ix:
                    maxVal = ix
            if abs(maxVal - iStatus) <= yThreshold:
                self.state = 'Split'
            elif abs(maxVal - jStatus) <= yThreshold:
                self.state = 'Move'
            else:   # abs(maxVal - kStatus) <= yThreshold:
                self.state = 'Die'
            # DEBUG
            print('split = ' + str(iStatus) + ', move = ' + str(jStatus) + '\ndie = ' + str(kStatus) + '. Max: '+ str(maxVal) + '\n')
    # GenerateStatus

    def Quiet(self,grid):
        grid[self.xPos][self.yPos][0] = 1
        self.quietCounter += 1
    # Quiet

    def Die(self, grid):
        self.amidead = True
        grid[self.xPos][self.yPos][0] = -1
    # Die

    def Move(self, grid):
        # check a randomly generated neighbour if occupied
        r = np.random.randint(4)
        # check if spot is occupied
        if r == 0:
            # each case returns the value on grid according to the random number (neighbour)
            newxPos = self.xPos - 1
            newyPos = self.yPos

        elif r == 1:
            newxPos = self.xPos
            newyPos = self.yPos + 1

        elif r == 2:
            newxPos = self.xPos + 1
            newyPos = self.yPos

        else:
            newxPos = self.xPos
            newyPos = self.yPos - 1

        occupation = grid[newxPos][newyPos][0]

        # if position if free, move there
        if occupation == 0:
            print('cell moved\n')
            grid[newxPos][newyPos][0] = 1
            grid[self.xPos][self.yPos][0] = 0
            self.xPos = newxPos
            self.yPos = newyPos
        else:
            print('move failed\n')
    # Move

    # OrientedMove, works with orientation ON and OFF
    def Move2(self, grid):
        # create a list with the four Von Neumann neighbours
        neighbourList = [[self.xPos - 1, self.yPos],[self.xPos + 1, self.yPos],[self.xPos, self.yPos - 1],[self.xPos, self.yPos + 1]]
        #finalList = []
        tmpList = []
        movePos = []
        needOtherNeighbours = True
        border = self.border - 1

        for neighbr in neighbourList:                               # for each possible neighbour:
            if CheckInBorders(neighbr[0], neighbr[1], border):      # if neighbour is inbunds:
                if CheckifOccupied(neighbr[0], neighbr[1], grid):   # if its occupied
                    print(str(neighbr) + ': neighbour occupied')
                    continue
                else:
                    xOri = self.orientation[0] 
                    yOri = self.orientation[1]
                    if CheckifPreferred(xOri, yOri, neighbr[0], neighbr[1]):    # if is preferred
                        movePos.append(neighbr[0])                  # if available, the return it as available
                        movePos.append(neighbr[1])
                        needOtherNeighbours = False                 # if available the no need to find more spots
                        print(str(neighbr) + ': preferred position available')
                        break                                       # and stop looking for available spots
                    else:
                        print(str(neighbr) + ': available neighbour')
                        tmpList.append(neighbr)                     # list with other available neighbours
            else:
                print(str(neighbr) + ': neighbour not in bounds')
                continue
        # if needed and if there's more than one spot available, the move to that spot 
        if needOtherNeighbours and len(tmpList) > 0:
            r = np.random.randint(len(tmpList))
            movePos.append(tmpList[r][0])
            movePos.append(tmpList[r][1])

        if len(movePos) > 0:
            grid[movePos[0]][movePos[1]][0] = 2                     # new position gets a 2 value to mark as moving cell
            grid[self.xPos][self.yPos][0] = -1                      # old position gets a -1 value to indicate that there was a cell there before
            self.xPos = movePos[0]                                  # update position
            self.yPos = movePos[1]
            print('cell moved!')
        else:
            grid[self.xPos][self.yPos][0] = 1                       # if moving fails then cell is marked as quiet
            print('moving failed\n')
    # Move2

    def Split(self, grid, cellList):
        self.splitCounter += 1
        if self.splitCounter == self.splitTime:
            self.splitCounter = 0
            # check a randomly generated neighbour if occupied
            r = np.random.randint(4)
            # check if spot is occupied
            if r == 0:
                # each case returns the value on grid according to the random number (neighbour)
                newxPos = self.xPos - 1
                newyPos = self.yPos
            elif r == 1:
                newxPos = self.xPos
                newyPos = self.yPos + 1
            elif r == 2:
                newxPos = self.xPos + 1
                newyPos = self.yPos
            else:
                newxPos = self.xPos
                newyPos = self.yPos - 1
            #occupation = grid[newxPos][newyPos][0]
            # if the position is free then create a cell there
            if grid[newxPos][newyPos][0] == 0:
                #	daughterCell = Cell(newxPos, newyPos)
                # DEBUG
                print('new cell created!\n')
                cellList.append(cell(newxPos, newyPos))
                grid[newxPos][newyPos][0] = 1
            else:
                print('split failed\n')
    # Split

    # works with polarisation ON and OFF
    # initial for and then if are the same as in Move2, might be useful to use a single function
    def Split2(self, grid, cellList):
        self.splitCounter += 1
        if self.splitCounter == self.splitTime:
            self.splitCounter = 0

            # create a list with the four Von Neumann neighbours
            neighbourList = [[self.xPos - 1, self.yPos],[self.xPos + 1, self.yPos],[self.xPos, self.yPos - 1],[self.xPos, self.yPos + 1]]
            #finalList = []
            tmpList = []
            movePos = []
            needOtherNeighbours = True
            border = self.border - 1

            for neighbr in neighbourList:                                           # for each possible neighbour:
                if CheckInBorders(neighbr[0], neighbr[1], border):                  # if neighbour is inbunds:
                    if CheckifOccupied(neighbr[0], neighbr[1], grid):               # if its occupied
                        print(str(neighbr) + ': neighbour occupied')
                        continue
                    else:
                        xOri = self.orientation[0] 
                        yOri = self.orientation[1]
                        if CheckifPreferred(xOri, yOri, neighbr[0], neighbr[1]):    # if is preferred
                            movePos.append(neighbr[0])                              # if available, the return it as available
                            movePos.append(neighbr[1])
                            needOtherNeighbours = False                             # if available the no need to find more spots
                            print(str(neighbr) + ': preferred position available')
                            break                                                   # and stop looking for available spots
                        else:
                            print(str(neighbr) + ': available neighbour')
                            tmpList.append(neighbr)                                 # list with other available neighbours
                else:
                    print(str(neighbr) + ': neighbour not in bounds')
                    continue
            # if needed and if there's more than one spot available, then move to that spot 
            if needOtherNeighbours and len(tmpList) > 0:
                r = np.random.randint(len(tmpList))
                movePos.append(tmpList[r][0])
                movePos.append(tmpList[r][1])
                #finalList.append(tmpList[r])
            if len(movePos) > 0:
                grid[self.xPos][self.yPos][0] = 3
                cellList.append(cell(movePos[0], movePos[1]))
                grid[movePos[0]][movePos[1]][0] = 1
                print('new cell created!')
            else:
                grid[self.xPos][self.yPos][0] = 1
                print('split failed\n')
        else:
            print('split counter + 1\n')
    # Split2
# Cell
