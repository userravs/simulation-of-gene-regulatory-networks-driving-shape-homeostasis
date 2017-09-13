import numpy as np
import matplotlib.pyplot as plt


class Environment:

	def CellsGridFigure(fieldSize)
		cellsFigure = plt.figure()		# initilize FIGURE, does is need name, figsize?

		cellsFigure.suptitle('Cell system')

		cellGrid = np.zeros([fieldSize, fieldSize])		# may need a new name, same as in main...
		sgfGrid = np.zeros([fieldSize, fieldSize])
		lgfGrid = np.zeros([fieldSize, fieldSize])

		cellsSubplot = cellsFigure.add_subplot(131)
		cellsSubplot.set_title('Cells') 

		sgfSubplot = cellsFigure.add_subplot(132)
		sgfSubplot.set_title('SGF') 

		lgfSubplot = cellsFigure.add_subplot(133)
		lgfSubplot.set_title('LGF') 

		plt.axis('off')

		cellPlot = cellsSubplot.imshow(cellGrid, origin = 'lower', cmap = 'PuOr', interpolation = 'none', vmin = -1, vmax = 1)
		sgfPlot = sgfSubplot.imshow(sgfGrid, origin = 'lower', cmap = 'binary', interpolation = 'none', vmin = 0, vmax = 10)
		lgfPlot = lgfSubplot.imshow(lgfGrid, origin = 'lower', cmap = 'binary', interpolation = 'none', vmin = 0, vmax = 10)

		plt.ion()
		plt.pause(0.001)
		cellsFigure.canvas.draw()
		plt.ioff()

		# function returns the figure, subplots and plots
		return cellsFigure, cellsSubplot, sgfSubplot, lgfSubplot, cellPlot, sgfPlot, lgfPlot
	#

	def AntGridPlot(terrainInfo, fieldSize, PlotDelay, 
				antsPlotHome, antsPlotFood, sugarPlot, nestPlot,
				antsSubPlot, antsFigure, nestPosition):    
		#======================================================================
		# Structure of the terrainInfo:
		#======================================================================
		# [agentState, agentHealth, sugarAmount]
		# [agentSate: 	0:foraging 
		#				1:ReturningHome
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
		AGENTSTATE = 0
		AGENTHEALTH = 1
		SUGARAMOUNT = 2
		AGENTFORAGING = 0
		AGENTRETURNINGHOME = 1		
		# AgentForaging position and state        
		npaAgentForagingPosX = np.array([])
		npaAgentForagingPosY = np.array([])
		npaAgentStateFor = np.array([])
		paAgentHealthFor = np.array([])
		# AgentRetHome position and state        
		npaAgentRetHomePosX = np.array([])
		npaAgentRetHomePosY = np.array([])
		npaAgentStateRet = np.array([])
		npaAgentHealthRetHome = np.array([])
		
		#=======================================================================
		# Get Information from terrainInfo,
		#=======================================================================
		for y in range(fieldSize):
			for x in range(fieldSize):
				# If HEALTH than there is a agent
				if terrainInfo[y,x,AGENTHEALTH] >= 1: 					
					# Recognise the foraging agent
					if terrainInfo[y,x,AGENTSTATE] == AGENTFORAGING: 
						npaAgentForagingPosX 	= np.append(npaAgentForagingPosX, np.array([x]))
						npaAgentForagingPosY 	= np.append(npaAgentForagingPosY, np.array([y]))
						npaAgentStateFor 		= np.append(npaAgentStateFor, terrainInfo[x,y,AGENTSTATE])
						paAgentHealthFor 		= np.append(paAgentHealthFor, terrainInfo[x,y,AGENTHEALTH])						
					# Recognise the returning agent
					if terrainInfo[y,x,AGENTSTATE] == AGENTRETURNINGHOME: 
						npaAgentRetHomePosX 	= np.append(npaAgentRetHomePosX, np.array([x]))
						npaAgentRetHomePosY 	= np.append(npaAgentRetHomePosY, np.array([y]))
						npaAgentStateRet 		= np.append(npaAgentStateRet, terrainInfo[x,y,AGENTSTATE])
						npaAgentHealthRetHome 	= np.append(npaAgentHealthRetHome, terrainInfo[x,y,AGENTHEALTH])
					#
				#
			#
		#		
		npaFoodAmount = terrainInfo[:,:,SUGARAMOUNT]
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		#=======================================================================		
		# Plots 
		#=======================================================================
		Environment.UpdatePlot(antsPlotFood, antsPlotHome, sugarPlot, nestPlot, nestPosition,
							antsSubPlot, antsFigure, 
							npaAgentForagingPosX, npaAgentForagingPosY,
							npaAgentRetHomePosX, npaAgentRetHomePosY,
							npaFoodAmount)
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#



	def UpdatePlot(antsPlot1, antsPlot2, sugarPlot, nestPlot, nestPosition,
				antsSubPlot, antsFigure, 
				new_dataX1, new_dataY1,
				new_dataX2, new_dataY2,
				new_data3):
		
		sugarPlot.set_data(new_data3)					
		antsPlot1.set_xdata(new_dataX1)
		antsPlot1.set_ydata(new_dataY1)
		antsPlot2.set_xdata(new_dataX2)
		antsPlot2.set_ydata(new_dataY2)	
		nestPlot.set_xdata(nestPosition)
		nestPlot.set_ydata(nestPosition)
		#	
		antsSubPlot.draw_artist(antsSubPlot.patch)
		antsSubPlot.draw_artist(sugarPlot)
		antsSubPlot.draw_artist(nestPlot)
		antsSubPlot.draw_artist(antsPlot1)
		antsSubPlot.draw_artist(antsPlot2)
		#
		antsFigure.canvas.update()
		antsFigure.canvas.flush_events()
	#
	
	
	
	def PheromoneGridFigure(fieldSize, 
				maxFoodPheromone, maxHomePheromone, 
				nestPosition=None):
		#=======================================================================
		# The Figure and the axis 
		# (This has to be outside of the loop for better performance)
		#======================================================================= 
		# Define the COLORMAPS for the plots
		cmapFood = plt.cm.get_cmap('YlOrRd')#('Blues')#('YlOrRd')
		cmapHome = plt.cm.get_cmap('YlGn')#('Blues')#('YlOrRd')   
		#
		figname='Pheromonetypes'
		figsizeX =18
		figSizeY = 9                
		figsize=(figsizeX,figSizeY)
		#
		pheromoneFigure = plt.figure(figname,figsize)	
		#			
		subPlot1_Home = pheromoneFigure.add_subplot(121)        
		subPlot1_Home.set_title('Pheromene 1 (finding the nest)',fontsize=30)
		subPlot1_Home.set_xlabel('x',fontsize=25)
		subPlot1_Home.set_ylabel('y',fontsize=25)
		#subPlot1_Home.grid(True,linestyle='-',color='0.75')
		subPlot1_Home.set_xlim(-0.5, fieldSize+0.5-1)
		subPlot1_Home.set_ylim(-0.5, fieldSize+0.5-1)  
		#
		subPlot2_Food = pheromoneFigure.add_subplot(122)
		subPlot2_Food.set_title('Pheromone 2 (foraging for food)',fontsize=30)
		subPlot2_Food.set_xlabel('x',fontsize=25)
		subPlot2_Food.set_ylabel('y',fontsize=25)
		#subPlot2_Food.grid(True,linestyle='-',color='0.75')
		subPlot2_Food.set_xlim(-0.5, fieldSize+0.5-1)
		subPlot2_Food.set_ylim(-0.5, fieldSize+0.5-1)   
		#
		imshowEmptyArray = np.zeros((fieldSize,fieldSize))  
		#
		pheroHomePlot = subPlot1_Home.imshow(
			                imshowEmptyArray, 
			                interpolation='none', 
			                cmap=cmapHome,
			                vmin=0, vmax=maxHomePheromone)
		#		
		plt.show(block=False)

		pheroFoodPlot = subPlot2_Food.imshow(
			                imshowEmptyArray, 
			                interpolation='none', 
			                cmap=cmapFood,
			                vmin=0, vmax=maxFoodPheromone)
		#       		
		plt.show(block=False)
		return subPlot1_Home, subPlot2_Food, pheromoneFigure, pheroHomePlot, pheroFoodPlot
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		
		
		
	def PheromoneGridPlot(pheromoneFigure, subPlot1_Home, subPlot2_Food,
						terrainInfo, fieldSize, PlotDelay,
						pheroHomePlot, pheroFoodPlot,
						nestPosition=None):   
		#=======================================================================
		# Add the data to the axis (Use this code while looping)
		# [Pheromone1, Pheromone2, sugarAmount]
		# get sugar amounts from terrainInfo
		#======================================================================= 
		PHEROMONE_HOME = 1
		PHEROMONE_FOOD = 0	
		#
		npaPHEROMONE_HOME = terrainInfo[:,:,PHEROMONE_HOME]
		#subPlot1_Home.draw_artist(subPlot1_Home.patch)			
		pheroHomePlot.set_data(npaPHEROMONE_HOME)	
		subPlot1_Home.draw_artist(pheroHomePlot)
		#
		npaPHEROMONE_FOOD = terrainInfo[:,:,PHEROMONE_FOOD]	
		#subPlot2_Food.draw_artist(subPlot2_Food.patch)
		pheroFoodPlot.set_data(npaPHEROMONE_FOOD)	
		subPlot2_Food.draw_artist(pheroFoodPlot)
		#
		pheromoneFigure.canvas.update()
		pheromoneFigure.canvas.flush_events()		
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#
