import numpy as np
import matplotlib.pyplot as plt
from tools import *

class cell:
	# defines whats needed when a new agent (Cell) of this class is created
	def __init__(self, xPos, yPos):
		self.xPos = xPos				# Initial position on x axis
		self.yPos = yPos				# Initial position on y axis
		self.splitCounter = 0				# Counter for splitting
		self.splitTime = 1				# Time scale for splitting
		self.quietCounter = 0				# Quiet counter
		self.orientation = [self.xPos,self.yPos]	# Preferred direction. DEFAULT: own position
		self.compass = False				# Polarisation: ON/OFF
		self.state = 'Quiet'				# State of the cell. DEFAULT: quiet
		self.border = 0					# size of the lattice
	# self

	#def Get Pos(self):
		#return

	# WARNING Do I use this method??
	def GetNeighbours(self, grid, border):
		neighbourList = []
		# TODO check if this works if orientation is OFF
		# if orientation is OFF the method returns the probable neighbours
		if self.xPos - 1 >= 0: # if coordinate is in-bounds
			if grid[self.xPos - 1, self.yPos][0] == 0 and self.orientation[0] != self.xPos - 1 and self.orientation[1] != self.yPos:
				# if is not occupied and not the preferred neighbour
				neighbourList.append([self.xPos - 1, self.yPos]) 
		if self.xPos + 1 <= border:
			if grid[self.xPos + 1, self.yPos][0] == 0 and self.orientation[0] != self.xPos + 1 and self.orientation[1] != self.yPos:
				neighbourList.append([self.xPos + 1, self.yPos])
		if self.yPos - 1 >= 0:
			if grid[self.xPos, self.yPos - 1][0] == 0 and self.orientation[0] != self.xPos and self.orientation[1] != self.yPos - 1:
				neighbourList.append([self.xPos, self.yPos - 1])
		if self.yPos + 1 <= border:
			if grid[self.xPos, self.yPos + 1][0] == 0 and self.orientation[0] != self.xPos and self.orientation[1] != self.yPos + 1:
				neighbourList.append([self.xPos, self.yPos + 1])
		# returns a list of possible neighbours which are not the prefered
		return neighbourList

	def CheckifPreferred(self, xCoord, yCoord):
		if xCoord == self.orientation[0] and self.orientation[1] == 1:
			return True
		else:
			return False
	# CheckifPreferred

	def Sense(self):
		# sense chemicals from the grid
		SGF_read = grid[self.xPos, self.yPos][1] # grid contains three values on each coordinate: 
		LGF_read = grid[self.xPos, self.yPos][2] # occupation (boolean), SGF level, LGF level
		#reads = [SGF_read, LGF_read]
		return SGF_read, LGF_read
	# Sense   
	
	def sgfProduce(self, grid, amount):
		grid[self.xPos, self.yPos][1] += amount 
	# sgfProduce

	def lgfProduce(self, grid, amount):
		grid[self.xPos, self.yPos][2] += amount 
	# lgfProduce

	def GenerateStatus(self, SGF_read, LGF_read):
		# neural network generates a status based on the reads
		border = self.border
		# possible states: split, move, die
		iStatus = np.random.random() 		# Proliferate:	Split
		jStatus = np.random.random() 		# Move:		Move
		kStatus = 0 #np.random.random() 	# Apoptosis:	Die
		# values for SGF and LGF
		sgfAmount = np.random.randint(5)
		lgfAmount = np.random.randint(5)

		# ORIENTATION:
		# randomly sets a preferred neighbour (polarisation)
		# if the direction is out of bounds then no preferred direction is stored 
		# WARNING This code need to be revisited depending on the implementation of the NN later on
		if self.compass:
			# boundaries for orientation
			nBoundary = 0.25
			sBoundary = 0.5
			eBoundary = 0.75
			#wBoundary = 1
			arrow = np.random.random()
			if arrow < nBoundary:
				xCoord = self.xPos - 1
				yCoord = self.yPos
				# orientation North
				if CheckInBorders(xCoord, yCoord, border):
					self.orientation = [xCoord, yCoord]
			elif arrow < sBoundary:
				# orientation South
				xCoord = self.xPos + 1
				yCoord = self.yPos
				# orientation North
				if CheckInBorders(xCoord, yCoord, border):
					self.orientation = [xCoord, yCoord]
			elif arrow < eBoundary:
				# orientation East
				xCoord = self.xPos
				yCoord = self.yPos + 1
				# orientation North
				if CheckInBorders(xCoord, yCoord, border):
					self.orientation = [xCoord, yCoord]
			else:	#arrow < wBoundary:
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
			else:	# abs(maxVal - kStatus) <= yThreshold:
				self.state = 'Die'
			# DEBUG
			print('split = ' + str(iStatus) + ', move = ' + str(jStatus) + '\ndie = ' + str(kStatus) + '. Max: '+ str(maxVal) + '\n')
	# GenerateStatus

	def Quiet(self):
		self.quietCounter += 1
	# Quiet
	
	def Die(self, grid):
		grid[self.xPos][self.yPos][0] = 0
	# Die
	
	# TODO or not...
	def OrientedMove(self, grid, cellList):
		print('ala')
	# OrientedMove
	
	def Move(self, grid):
		# check a randomly generated neighbour if occupied
		print('moving!!')
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

	# TEST!!!	OrientedMove, works with orientation ON and OFF
	def Move2(self, grid):
		# create a list with the four Von Neumann neighbours
		neighbourList = [[self.xPos - 1, self.yPos],[self.xPos + 1, self.yPos],[self.xPos, self.yPos - 1],[self.xPos, self.yPos + 1]]
		#finalList = []
		tmpList = []
		movePos = []
		needOtherNeighbours = True
		border = self.border

		for neighbr in neighbourList: 						# for each possible neighbour:
			if CheckInBorders(neighbr[0], neighbr[1], border):		# if neighbour is inbunds:
				if CheckifOccupied(neighbr[0], neighbr[1], grid):	# if its occupied
					continue
				else:
					if CheckifPreferred(neighbr[0], neighbr[1]):	# if is preferred
						movePos.append(neighbr[0])		# if available, the return it as available
						movePos.append(neighbr[1])
						needOtherNeighbours = False		# if available the no need to find more spots
						break					# and stop looking for available spots
					else:
						tmpList.append(neighbr)			# list with other available neighbours
			else:
				continue
		# if needed and if there's more than one spot available, the move to that spot 
		if needOtherNeighbours and len(tmpList) > 0:
			r = np.random.randint(len(tmpList))
			movePos.append(tmpList[r][0])
			movePos.append(tmpList[r][1])
			#finalList.append(tmpList[r])
		if len(movePos) > 0:
			grid[movePos[0]][movePos[1]][0] = 1
			grid[self.xPos][self.yPos][0] = 0
			self.xPos = movePos[0]
			self.yPos = movePos[1]
	# Move2

	# TODO
	def OrientedSplit(self, grid, cellList):
		print('ala')	
	# OrientedSplit

	def Split(self, grid, cellList):
		print('splitting!!')
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

	# TEST!! works with polarisation ON and OFF
	# initial for and then if are the same as in Move2, might be useful to use a single function
	def Split2(self, grid, cellList):
		# create a list with the four Von Neumann neighbours
		neighbourList = [[self.xPos - 1, self.yPos],[self.xPos + 1, self.yPos],[self.xPos, self.yPos - 1],[self.xPos, self.yPos + 1]]
		#finalList = []
		tmpList = []
		movePos = []
		needOtherNeighbours = True
		border = self.border

		for neighbr in neighbourList: 						# for each possible neighbour:
			if CheckInBorders(neighbr[0], neighbr[1], border):		# if neighbour is inbunds:
				if CheckifOccupied(neighbr[0], neighbr[1], grid):	# if its occupied
					continue
				else:
					if CheckifPreferred(neighbr[0], neighbr[1]):	# if is preferred
						movePos.append(neighbr[0])		# if available, the return it as available
						movePos.append(neighbr[1])
						needOtherNeighbours = False		# if available the no need to find more spots
						break					# and stop looking for available spots
					else:
						tmpList.append(neighbr)			# list with other available neighbours
			else:
				continue
		# if needed and if there's more than one spot available, then move to that spot 
		if needOtherNeighbours and len(tmpList) > 0:
			r = np.random.randint(len(tmpList))
			movePos.append(tmpList[r][0])
			movePos.append(tmpList[r][1])
			#finalList.append(tmpList[r])
		if len(movePos) > 0:
			cellList.append(cell(movePos[0], movePos[1]))
			grid[movePos[0]][movePos[1]][0] = 1
	# Split2
# Cell
