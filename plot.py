import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
#from mpl_toolkits.axes_grid1 import ImageGrid

class Environment:

    def CellsGridFigure(fieldSize, mode):
        # mode = True: cell_system as fitness function
        # mode = False: cell_system as display system
        plt.close()

        #discrete color scheme
        cMap = ListedColormap(['w', 'g', 'b', 'r'])

        cellsFigure, (cellsSubplot,sgfSubplot,lgfSubplot) = plt.subplots(1, 3, figsize = (15,5))

        cellsSubplot.set_aspect('equal')                        # TODO does this work?
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

        cellPlot = cellsSubplot.imshow(cellGrid, origin = 'lower', cmap = cMap, interpolation = 'none', vmin = 0, vmax = 3)
        cbar1 = cellsFigure.colorbar(cellPlot, ax = cellsSubplot, ticks = [], orientation='horizontal')#, shrink=0.75)
        #cbar1.ax.set_yticklabels(['dead', 'quiet', 'moving', 'splitting'])
        ##legend
        #cbar = plt.colorbar(cellPlot)

        cellPlot.axes.xaxis.set_ticklabels([])
        cellPlot.axes.yaxis.set_ticklabels([])
#        cellPlot.axes.get_xaxis().set_visible(False)
#        cellPlot.axes.get_yaxis().set_visible(False)

        cbar1.ax.get_yaxis().set_ticks([])
        for j, lab in enumerate(['$empty$','$quiet$','$moving$','$divided$']):
            cbar1.ax.text((2 * j + 1) / 8.0, .5, lab, ha = 'center', va = 'center')#, rotation=270)
        cbar1.ax.get_yaxis().labelpad = 15
        cbar1.ax.set_ylabel('states', rotation = 270)

        sgfPlot = sgfSubplot.imshow(sgfGrid, origin = 'lower', cmap = 'Reds', interpolation = 'none', vmin = 0, vmax = 3)
        cbar2 = cellsFigure.colorbar(sgfPlot, ax = sgfSubplot, orientation = 'horizontal')

        lgfPlot = lgfSubplot.imshow(lgfGrid, origin = 'lower', cmap = 'Blues', interpolation = 'none', vmin = 0, vmax = 3)
        cbar3 = cellsFigure.colorbar(lgfPlot, ax = lgfSubplot, orientation = 'horizontal')

        if mode == False:
            plt.show(block = False)

        plt.ion()
        #plt.pause(0.001)
        cellsFigure.canvas.draw()
        plt.ioff()

        # function returns the figure, subplots and plots
        return cellsFigure, cellsSubplot, sgfSubplot, lgfSubplot, cellPlot, sgfPlot, lgfPlot
    # CellsGridFigure

    def AntGridPlot(cellGrid,
                    chemGrid,
                    nLattice,
                    cellsFigure,
                    cellsSubplot,
                    sgfSubplot,
                    lgfSubplot,
                    cellPlot,
                    sgfPlot,
                    lgfPlot,
                    tStep,
                    mode):

        cell_data = cellGrid         # slice the grid to get the layer with the cell positions
        sgf_data = chemGrid[:,:,0]          # slice the grid to get the layer with the SGF profile
        lgf_data = chemGrid[:,:,1]          # slice the grid to get the layer with the LGF profile

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
                                tStep,
                                mode)

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
                    tStep,
                    mode):
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

        #if mode == True:
        #    plt.savefig('CA_gen' + '{:02d}'.format(iGen) + '_ind' + '{:02d}'.format(individual) +'_tstep' + '{:03d}'.format(tStep) + '.png', bbox_inches='tight')
    # UpdatePlot
# Environment

def StatsPlot(statsFile):
    varSpace = 2
    nGen = 10
    with open('stats/{}'.format(statsFile), 'r') as dataFile:
        statsArray = np.loadtxt(dataFile,delimiter=',')
        statsArray = statsArray.reshape(varSpace, nGen, 2)

    #dataFigure, (dataSubplot) = plt.subplots(1, 1, figsize = (15,5))

    plt.close()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #fig.suptitle('')
    genList = np.arange(1, nGen+1) #np.arange(nGen)
    # xticks = 
    ax.set_xlabel('number of generations')
    ax.set_ylabel('fitness')
    ax.set_xticks(genList)
    #ax.set_xscale('log')
    #ax.set_yscale('log')
    
    ax.set_title('change in fitness over generations')   
    ax.plot(genList, statsArray[0,:,1], 'r--', label='8 nodes')
    ax.plot(genList, statsArray[1,:,1], 'b-', label='25 nodes')
    ax.scatter(genList, statsArray[0,:,0], label='max fitness')
    ax.scatter(genList, statsArray[1,:,0], label='max fitness')
    # ax.plot(syntheticForest,normRank,label='Synthetic data')
    ax.legend(loc = 'best')
    #plt.savefig('fire_vs_synthetic_datatic-p'+str(p)+'-f'+str(f)+'.png')
    plt.show()
    
    
if __name__ == '__main__':
    dataFile = sys.argv[1]
    StatsPlot(dataFile)
