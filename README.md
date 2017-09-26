

# CA

## Useful links
* Diffusion equation with python: https://hinderedsettling.com/2015/02/06/exploring-the-diffusion-equation-with-python/

## Useful commands
* ffmpeg -f image2 -pattern_type glob -framerate 24 -i 'cell_system-*.png' -s 1024x1024 cell_system.avi

## Thesis events
### 20170901: Started working 
* Cell in a grid capable to reproduce.

### 20170907:
* Plotting works: unefficient way, must improve this!
* Adding states: move, split, die. Start to work on cell dynamics and then insert the neural network

### 20170911:
* Added new functions for moving and splitting. In principle they work regardless of the state of the compass (ON/OFF). Must test that.
* Must clarify the decision making: what happens if the orientation direction is out of bounds or occupied? action must fail or choose a random available spot instead?

### 20170913:
* Started implementing the more stable and fast plotting scheme.
* Read some articles about NN. Must:
	* Do some research about which type of NN is adequate for the model.
	* Is the NN used originally in the model the best for the task?
	* Should I use available libraries or write my own code for NN.
	* Think about how to record a video/timelapse of the cell structure

### 20170914:
* Fixed plotting. Now works like a charm. Fast and smooth.
* Fixed move2 and split2 functions. Borders of the grid and orientation. Orientation needs some testing though.
* Need to fix the Die method

### 20170920:
#### Done:
* Die method is correct now
* Dynamics for SGF.
* Code cleaning.
* Now I'm using the following code for the grid:
	* -1: There was a cell on this spot before but muved away or died.
	* 0: spot has been always empty.
	* 1: a quiet cell lies here
	* 2: a cell moved to this spot
	* 3: cell just gave birth
#### To do:
* Double check action functions: quiet, move, die, split, generateStatus, orientation system
* Test decaying dynamics of SGF.
* Implement dynamics for LGF.
* Implement self-made NN.

### 20170921
#### To do:
* Write more comments in the code, everything should be as clear as possible.
* Have to update the SGF and LGF via matrix operations.
* Draw a flow diagram of the main code. (!)

### 20170925
#### Done:
* Cleaning of repo, code.
* Implemented matrix scheme of SGF and LGF dynamics. Needs testing!
* Flow diagrams have sketch.

#### To do:
* Test every cell action and SGF/LGF dynamics.
* Start implementation of NN.
* Digital version of flow charts.
* Discuss order of updates in cell dynamics.

### 20170926
#### Done:
* NN implemented. 
* Corrected some bugs in split, move and die actions.

#### To do:
* Test NN. Use a working example if possible, otherwise start implementaion of EA.
* EA.
* Fix order of coordinates x, y. Not a big issue but leads to some confusion.
* Use a better color combination for cell states. Colorblind proof
