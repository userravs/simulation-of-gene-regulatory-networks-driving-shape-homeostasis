import numpy as np
import matplotlib.pyplot as plt


class Environment:

	def CellsGridFigure(fieldSize):
		cellsFigure = plt.figure(figsize=(15,5))				# initilize FIGURE, does is need name, figsize?

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
		plt.show(block=False)
		sgfPlot = sgfSubplot.imshow(sgfGrid, origin = 'lower', cmap = 'binary', interpolation = 'none', vmin = 0, vmax = 10)
		plt.show(block=False)
		lgfPlot = lgfSubplot.imshow(lgfGrid, origin = 'lower', cmap = 'binary', interpolation = 'none', vmin = 0, vmax = 10)
		plt.show(block=False)

		plt.ion()
		plt.pause(0.001)
		cellsFigure.canvas.draw()
		plt.ioff()

		# function returns the figure, subplots and plots
		return cellsFigure, cellsSubplot, sgfSubplot, lgfSubplot, cellPlot, sgfPlot, lgfPlot
	# CellsGridFigure

	def AntGridPlot(cellGrid,
			nLattice,
			cellsFigure, 
			cellsSubplot, 
			sgfSubplot, 
			lgfSubplot, 
			cellPlot, 
			sgfPlot, 
			lgfPlot):

		cell_data = cellGrid[:,:,0] 		# slice the grid to get the layer with the cell positions
		sgf_data = cellGrid[:,:,1] 		# slice the grid to get the layer with the cell positions
		lgf_data = cellGrid[:,:,2] 		# slice the grid to get the layer with the cell positions

		Environment.UpdatePlot(cellsFigure, cellsSubplot, sgfSubplot, lgfSubplot, cellPlot, sgfPlot, lgfPlot, cell_data, sgf_data, lgf_data)

	def UpdatePlot(	cellsFigure, 
			cellsSubplot, 
			sgfSubplot, 
			lgfSubplot, 
			cellPlot, 
			sgfPlot, 
			lgfPlot,
			cell_data, 
			sgf_data,
			lgf_data):
		#
		cellPlot.set_data(cell_data)
		sgfPlot.set_data(sgf_data)
		lgfPlot.set_data(lgf_data)
		#
		cellsSubplot.draw_artist(cellsSubplot.patch)
		cellsSubplot.draw_artist(cellPlot)
		sgfSubplot.draw_artist(sgfPlot)
		lgfSubplot.draw_artist(lgfPlot)
		#
		cellsFigure.canvas.update()
		cellsFigure.canvas.flush_events()
	# UpdatePlot
# Environment
