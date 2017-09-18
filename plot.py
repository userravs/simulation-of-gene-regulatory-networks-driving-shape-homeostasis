import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import ImageGrid

class Environment:

    def CellsGridFigure(fieldSize):
        plt.close()
        
        #discrete color scheme
        lala8 = ListedColormap(['w', 'g', 'b', 'r'])
        #ListedColormap(['white', 'green', 'blue','red'], name = 'cell_cMap')
        #colors = ["white", "green", "blue", "red"]
        #cmap = ListedColormap(colors)

        cellsFigure = plt.figure(figsize=(15,5))                # initilize FIGURE, does is need name, figsize?

        cellsFigure.suptitle('Cell system')

        cellGrid = np.zeros([fieldSize, fieldSize])             # may need a new name, same as in main...
        sgfGrid = np.zeros([fieldSize, fieldSize])
        lgfGrid = np.zeros([fieldSize, fieldSize])

        cellsSubplot = cellsFigure.add_subplot(131)
        cellsSubplot.set_title('Cells') 

        sgfSubplot = cellsFigure.add_subplot(132)
        sgfSubplot.set_title('SGF') 

        lgfSubplot = cellsFigure.add_subplot(133)
        lgfSubplot.set_title('LGF') 

    #   plt.axis('off')
        
        #heatmap = cellsSubplot.pcolor(data, cmap=cMap)
        
        cellPlot = cellsSubplot.imshow(cellGrid, origin = 'lower', cmap = lala8, interpolation = 'none', vmin = 0, vmax = 3)
        
        #legend
        cbar = plt.colorbar(cellPlot)
        cbar.cellsSubplot.get_yaxis().set_ticks([])
        for j, lab in enumerate(['$dead$','$quiet$','$moving$','$divided$']):
            cbar.cellsSubplot.text(.5, (2 * j + 1) / 8.0, lab, ha='center', va='center')
        cbar.cellsSubplot.get_yaxis().labelpad = 15
        cbar.cellsSubplot.set_ylabel('state', rotation=270)
        
        #cbar1 = colorbar(cellPlot, ticks = [0, 1, 2, 3]) bwr
        #cellsSubplot.set_yticklabels(['no cell', 'quiet', 'moved', 'splitted'])  # vertically oriented colorbar
        plt.show(block=False)

        sgfPlot = sgfSubplot.imshow(sgfGrid, origin = 'lower', cmap = 'binary', interpolation = 'none', vmin = 0, vmax = 50)
        #cbar2 = cellsFigure.colorbar(sgfPlot) #, ticks=[0, 1, 2, 3])
        #cbar2.sgfPlot.set_yticklabels(['no cell', 'quiet', 'moved', 'splitted'])  # vertically oriented colorbar        
        plt.show(block=False)

        lgfPlot = lgfSubplot.imshow(lgfGrid, origin = 'lower', cmap = 'binary', interpolation = 'none', vmin = 0, vmax = 50)
        #cbar3 = cellsFigure.colorbar(lgfPlot) #, ticks=[0, 1, 2, 3])
        #cbar3.lgfPlot.set_yticklabels(['no cell', 'quiet', 'moved', 'splitted'])  # vertically oriented colorbar
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
            lgfPlot,tStep):

        cell_data = cellGrid[:,:,0] 		# slice the grid to get the layer with the cell positions
        sgf_data = cellGrid[:,:,1] 		# slice the grid to get the layer with the cell positions
        lgf_data = cellGrid[:,:,2] 		# slice the grid to get the layer with the cell positions

        Environment.UpdatePlot(cellsFigure, cellsSubplot, sgfSubplot, lgfSubplot, cellPlot, sgfPlot, lgfPlot, cell_data, sgf_data, lgf_data,tStep)

    def UpdatePlot( cellsFigure, 
                    cellsSubplot, 
                    sgfSubplot, 
                    lgfSubplot, 
                    cellPlot, 
                    sgfPlot, 
                    lgfPlot,
                    cell_data, 
                    sgf_data,
                    lgf_data,tStep):
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
        #plt.savefig('cell_system-' + '{:03d}'.format(tStep) + '.png', bbox_inches='tight')
    # UpdatePlot
    # Environment
