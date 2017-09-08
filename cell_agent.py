####################################################
import numpy as np
import matplotlib.pyplot as plt

class cell:
	# defines whats needed when a new agent (Cell) of this class is created
	def __init__(self, xPos, yPos):
		self.xPos = xPos
		self.yPos = yPos
		self.splitCounter = 0
		self.splitTime = 1
		self.quietCounter = 0
		#self.state = status
	# self

	#def Get Pos(self):
		#return

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
		#sgfAmount = np.random.randint(5)
		# orientation
		#polarisation: np.random.randint(4)
		
		maxVal = 0.5
		#tmpVal = 0
		xThreshold = 0.5
		yThreshold = 0.01
		
		if iStatus < xThreshold and jStatus < xThreshold and kStatus < xThreshold:
			state = 'Quiet'
		
		else:
			for ix in iStatus, jStatus, kStatus:
				if maxVal < ix:
					maxVal = ix
			
			print('split = ' + str(iStatus) + ', move = ' + str(jStatus) + '\ndie = ' + str(kStatus) + '. Max: '+ str(maxVal))
		
			if abs(maxVal - iStatus) <= yThreshold:
				state = 'Split'

			elif abs(maxVal - jStatus) <= yThreshold:
				state = 'Move'
		
			else:	# abs(maxVal - kStatus) <= yThreshold:
				state = 'Die'		
			
		return state
	# GenerateStatus

	def Quiet(self,grid, cellList):
		self.quietCounter += 1
	# Quiet
	
	def Die(self,  grid, cellList):
		grid[self.xPos][self.yPos] = 0
	# Die
	
	def OrientedMove(self, grid, cellList, orientation):
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

		occupation = grid[newxPos][newyPos]		
		
		# if position if free, move there
		if occupation == 0:
			grid[newxPos][newyPos] = 1
			grid[self.xPos][self.yPos] = 0
			self.xPos = newxPos
			self.yPos = newyPos
	# Move

	def OrientedSplit(self, grid, cellList, orientation):
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

			occupation = grid[newxPos][newyPos]

				# if the position is free then create a cell there
			if occupation == 0:
				#	daughterCell = Cell(newxPos, newyPos)
				cellList.append(cell(newxPos, newyPos))
				grid[newxPos][newyPos] = 1
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
