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

        #cellsFigure = plt.figure(figsize=(15,5))                # initilize FIGURE, does is need name, figsize?
        cellsFigure, (cellsSubplot,sgfSubplot,lgfSubplot) = plt.subplots(1, 3, figsize = (15,5))

        cellsSubplot.set_aspect('equal')
        sgfSubplot.set_aspect('equal')
        lgfSubplot.set_aspect('equal')

        cellsFigure.suptitle('Cell system')

        cellGrid = np.zeros([fieldSize, fieldSize])             # may need a new name, same as in main...
        sgfGrid = np.zeros([fieldSize, fieldSize])
        lgfGrid = np.zeros([fieldSize, fieldSize])


        cellsSubplot.set_title('Cells')

#        cellsSubplot.axis('off')

        sgfSubplot.set_title('SGF')
#        sgfSubplot.axis('off')

        lgfSubplot.set_title('LGF')
 #       lgfSubplot.axis('off')
        
        cellPlot = cellsSubplot.imshow(cellGrid, origin = 'lower', cmap = lala8, interpolation = 'none', vmin = 0, vmax = 3)
        cbar1 = cellsFigure.colorbar(cellPlot, ax=cellsSubplot, ticks=[0, 1, 2, 3], orientation='horizontal')#, shrink=0.75)
        #cbar1.ax.set_yticklabels(['dead', 'quiet', 'moving', 'splitting'])
        ##legend
        #cbar = plt.colorbar(cellPlot)

        cellPlot.axes.xaxis.set_ticklabels([])
        cellPlot.axes.yaxis.set_ticklabels([])
#        cellPlot.axes.get_xaxis().set_visible(False)
#        cellPlot.axes.get_yaxis().set_visible(False)

        cbar1.ax.get_yaxis().set_ticks([])
        for j, lab in enumerate(['$dead$','$quiet$','$moving$','$divided$']):
            cbar1.ax.text((2 * j + 1) / 8.0, .5, lab, ha='center', va='center')#, rotation=270)
        cbar1.ax.get_yaxis().labelpad = 15
        cbar1.ax.set_ylabel('states', rotation=270)
        
        sgfPlot = sgfSubplot.imshow(sgfGrid, origin = 'lower', cmap = 'Blues', interpolation = 'none', vmin = 0, vmax = 8)
        cbar2 = cellsFigure.colorbar(sgfPlot, ax=sgfSubplot, orientation='horizontal')

        lgfPlot = lgfSubplot.imshow(lgfGrid, origin = 'lower', cmap = 'Reds', interpolation = 'none', vmin = 0, vmax = 100)
        cbar3 = cellsFigure.colorbar(lgfPlot, ax=lgfSubplot, orientation='horizontal')

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
                    lgfPlot,
                    tStep):

        cell_data = cellGrid[:,:,0]         # slice the grid to get the layer with the cell positions
        sgf_data = cellGrid[:,:,1]          # slice the grid to get the layer with the SGF profile
        lgf_data = cellGrid[:,:,2]          # slice the grid to get the layer with the LGF profile

        Environment.UpdatePlot( cellsFigure,
                                cellsSubplot,
                                sgfSubplot,
                                lgfSubplot,
                                cellPlot,
                                sgfPlot,
                                lgfPlot,
                                cell_data,
                                sgf_data,
                                lgf_data,
                                tStep)

    def UpdatePlot( cellsFigure, 
                    cellsSubplot, 
                    sgfSubplot, 
                    lgfSubplot, 
                    cellPlot, 
                    sgfPlot, 
                    lgfPlot,
                    cell_data, 
                    sgf_data,
                    lgf_data,
                    tStep):
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
