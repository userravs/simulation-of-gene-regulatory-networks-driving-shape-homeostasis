import numpy as np
import matplotlib.pyplot as plt

class cell:
	# defines whats needed when a new agent (Cell) of this class is created
	def __init__(self, xPos, yPos):
		self.xPos = xPos							# Initial position on x axis
		self.yPos = yPos							# Initial position on y axis
		self.splitCounter = 0						# Counter for splitting
		self.splitTime = 1							# Time scale for splitting
		self.quietCounter = 0						# Quiet counter
		self.orientation = [self.xPos,self.yPos]	# Preferred direction. DEFAULT: own position
		self.compass = False						# Polarisation ON/OFF
		self.state = 'Quiet'						# Sate of the cell. DEFAULT: quiet
	# self

	#def Get Pos(self):
		#return

	# TODO pass lattice size information to this method
	# 
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

	# Functions used to deal with neighbours
	def CheckInBorders(self, xCoord, yCoord, border)
		if xCoord - 1 >= 0 and xCoord + 1 <= border: 	# Check if the neighbour is inbounds on x axis
			return False
		elif yCoord - 1 >= 0 and yCoord + 1 <= border:	# Check if the neighbour is inbounds on y axis
			return False
		else:
			return True
		# CheckInBorders

	def CheckifPreferred(self, xCoord, yCoord):
		if xCoord == self.orientation[0] and self.orientation[1] == 1:
			return True
		else:
			return False
	# CheckifPreferred

	def CheckifOccupied(self, xCoord, yCoord, grid):
		if grid[xCoord, yCoord][0] == 1:
			return True
		else:
			return False
	# CheckifOccupied

	def Sense(self):
		# sense chemicals from the grid
		SGF_read = grid[self.xPos, self.yPos][1] # grid contains three values on each coordinate: occupation (boolean), SGF level, LGF level
		LGF_read = grid[self.xPos, self.yPos][2]
		#reads = [SGF_read, LGF_read]
		return SGF_read, LGF_read
	# Sense   

	def GenerateStatus(self, SGF_read, LGF_read):
		# neural network generates a status based on the reads
		
		# possible states: split, move, die
		iStatus = np.random.random() # Proliferate	Split
		jStatus = np.random.random() # Move			Move
		kStatus = 0 #np.random.random() # Apoptosis	Die
		# values for SGF and LGF
		#sgfAmount = np.random.randint(5)
		#lgfAmount = np.random.randint(5)

		# orientation		
		# TODO: orientation should be inside borders
		if self.compass == True:
			# boundaries for orientation
			nBoundary = 0.25
			sBoundary = 0.5
			eBoundary = 0.75
			#wBoundary = 1
			arrow = np.random.random()
			if arrow < nBoundary:
				# orientation North
				self.orientation = [self.xPos - 1,self.yPos]
			elif arrow < sBoundary:
				# orientation South
				self.orientation = [self.xPos + 1,self.yPos]	
			elif arrow < eBoundary:
				# orientation East
				self.orientation = [self.xPos,self.yPos + 1]
			else:	#arrow < wBoundary:
				# orientation West
				self.orientation = [self.xPos,self.yPos - 1]				
			#else:
			#	# orientation OFF
			#	self.orientation = [self.xPos,self.yPos]				

		# Generate state
		maxVal = 0.5
		#tmpVal = 0
		xThreshold = 0.5
		yThreshold = 0.01
		
		if iStatus < xThreshold and jStatus < xThreshold and kStatus < xThreshold:
			self.state = 'Quiet'
		
		else:
			for ix in iStatus, jStatus, kStatus:
				if maxVal < ix:
					maxVal = ix
			
			# DEBUG
			print('split = ' + str(iStatus) + ', move = ' + str(jStatus) + '\ndie = ' + str(kStatus) + '. Max: '+ str(maxVal))
		
			if abs(maxVal - iStatus) <= yThreshold:
				self.state = 'Split'

			elif abs(maxVal - jStatus) <= yThreshold:
				self.state = 'Move'
		
			else:	# abs(maxVal - kStatus) <= yThreshold:
				self.state = 'Die'		
			
		#return state
	# GenerateStatus

	def Quiet(self, grid, cellList):
		self.quietCounter += 1
	# Quiet
	
	def Die(self, grid, cellList):
		grid[self.xPos][self.yPos][0] = 0
	# Die
	
	# TODO
	def OrientedMove(self, grid, cellList):
		print('ala')
	# OrientedMove
	
	def Move(self, grid, cellList):
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
			grid[newxPos][newyPos][0] = 1
			grid[self.xPos][self.yPos][0] = 0
			self.xPos = newxPos
			self.yPos = newyPos
	# Move
	
	# TODO: consider borders of the grid
	def Move2(self, grid, cellList):
		neighbourList = self.GetNeighbours(grid, border)
		if len(neighbourList) > 0:
			tmpNeighbList = list(neighbourList) 
			r = np.random.randint(len(tmpNeighbList))
	# Move2

	# TODO
	def OrientedSplit(self, grid, cellList):
		print('ala')	
	# OrientedSplit

	def Split(self, grid, cellList):
		self.splitCounter +=1
		if self.splitCounter == self.splitTime:
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

			# if the position is free then create a cell there
			if occupation == 0:
				#	daughterCell = Cell(newxPos, newyPos)
				cellList.append(cell(newxPos, newyPos))
				grid[newxPos][newyPos][0] = 1
				#	return grid
#		else
#			return grid
# Cell
	#def GetPos(self):
	#	return [self.xPos,self.yPos]
	# Split

class environment:
	def AntGridFigure(fieldSize, maxFoodAmount, nestPosition):    
		'''
		This method has to be called before the looping occours, for a better performance.
		Inspired by:
		http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
		'''
		#=======================================================================
		# The Figure
		#======================================================================= 
		# Grid:	
		cmapGrid = plt.cm.get_cmap('cool')#('PiYG_r')#('YlOrRd')#('Blues')#('YlOrRd')
		figname='Environment'					# main title for plot
		figsizeX =18						# outer plot dimensions
		figSizeY = 9                
		figsize=(figsizeX,figSizeY)
		cellsFigure = plt.figure(figname,figsize)		# declare main (outer) plot
		cellsSubPlot = cellsFigure.add_subplot(111)     	# add subplot: cell grid
		cellsSubPlot.set_aspect('equal')			# settings for grid 
		cellsSubPlot.set_title('Environment',fontsize=32)
		cellsSubPlot.set_xlabel('x',fontsize=25)
		cellsSubPlot.set_ylabel('y',fontsize=25)
		#cellsSubPlot.grid(True,linestyle='-',color='0.75')
		cellsSubPlot.set_xlim(-0.5, fieldSize+0.5-1)
		cellsSubPlot.set_ylim(-0.5, fieldSize+0.5-1)     
		plt.axis('off')
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~		
		npaAgentForagingPosY = np.array([0])
		npaAgentForagingPosX = np.array([0])
		npaFoodAmount = np.zeros((fieldSize,fieldSize))
		#
		gridPlot = cellsSubPlot.imshow(npaFoodAmount, interpolation='none', cmap=cmapGrid, vmin=0, vmax=maxFoodAmount)
		cellsPlotFood, 	= cellsSubPlot.plot(npaAgentForagingPosY, npaAgentForagingPosX, 'p', ms=7, color='orange', label='cells foraging')
		antPlotHome, 	= cellsSubPlot.plot(npaAgentForagingPosY, npaAgentForagingPosX, 'o', ms=10, color='blue', label='cells returning home')	
		nestPlot, 		= cellsSubPlot.plot(nestPosition,nestPosition, 'o', ms=30, color='black', label='Nest')	
		# Legend
		handles, labels = cellsSubPlot.get_legend_handles_labels()
		display = (0,1,2)

		
		# Now add the legend with some customizations.
		cellsSubPlot.legend(numpoints=1, shadow=True, bbox_to_anchor=(0,0,-0.05, 1), fontsize=25)
		
		#=======================================================================
		# # Create custom artists
		# #cellsSubPlot.legend(scatterpoints=1, bbox_to_anchor=(0,0,-0.05, 1))
		# cellsForaging 		= plt.Line2D((0,1),(0,0), color='violet', marker='p')
		# cellsReturningHome 	= plt.Line2D((0,1),(0,0), color='blue', marker='o')
		# nest				= plt.Line2D((0,1),(0,0), color='black', marker='o')
		# #food				= plt.Line2D((0,1),(0,0), color='black', marker='s')
		# # Create legend from custom artist/label lists
		# cellsSubPlot.legend([handle for i,handle in enumerate(handles) if i in display]+[cellsForaging,cellsReturningHome,nest],
		# 					[label for i,label in enumerate(labels) if i in display]+['cells foraging', 'cells returning home', 'Nest'],
		# 					numpoints=1, bbox_to_anchor=(0,0,-0.05, 1))
		#=======================================================================

		#
		img = plt.imshow(np.array([[0,1]]), cmap=cmapGrid)
		img.set_visible(False)		
		cbarAmountGrid = plt.colorbar(orientation="vertical")
		cbarAmountGrid.set_label('Amount of food',size=25)
		#
		plt.ion()
		plt.pause(0.0001)
		cellsFigure.canvas.draw()
		plt.ioff()
		#
		return cellsSubPlot, cellsFigure, cellsPlotFood, antPlotHome, gridPlot, nestPlot
	#
# Environment
