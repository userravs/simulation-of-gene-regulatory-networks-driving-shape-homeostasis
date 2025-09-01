

# Gene Regulatory Networks Driving Shape Homeostasis - Development History

## Project Overview
This document tracks the development history of the Gene Regulatory Networks (GRN) simulation project, from initial implementation to the current containerized web interface.

## Useful Links
* Diffusion equation with python: https://hinderedsettling.com/2015/02/06/exploring-the-diffusion-equation-with-python/
* Streamlit documentation: https://docs.streamlit.io/
* Docker documentation: https://docs.docker.com/

## Useful Commands
* ffmpeg -f image2 -pattern_type glob -framerate 24 -i 'cell_system-*.png' -s 1024x1024 cell_system.avi
* Docker: `./run_docker.sh` - Start the web interface
* Web interface: http://localhost:8501

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

### 20171004
#### Done:
* Implemented correct dynamics for Recurrent Neural Network.
* In principle, done with GA.
* main.py as function called by main_ga.py
* GA functions: fitness, crossover, mutate, elitism, tournament selection.
* Read/write code to store rNN and to read it later.

#### To do:
* TEST the WHOLE thing...
* decide where to hardcode stuff and where to leave it general.
* Improve performance.
* write a script (bash?) to run for all different parameter combinations.
* Implement a True/False switch for the different plotting actions: store some snapshots or plot every time step

### 20171005
#### Done:
* After some test runs the following has been concluded:
	* The offspring generation scheme may not be the best. Crossover is too efficient and the solutions go to a local minimum very quickly.
	* The GA could be easily paralelized distributing the individuals to all processors and letting each run the simulation by itself and then sending the fitness value to the master.
	* Inside the simulation might be useful to implement some CUDA code since it's all matrix operations. But on the other hand, numpy might be good enough.
	* The fitness function is the simulation itself sort of. It compares the structure of the system halfway and at the end of the simulation. This is a bit forced, there has to be a smarter way to do this.
* Code cleaning
* Implement the double functionality of main.py, as module or as a main code.

#### To do:
* Think about the ideas mentioned above for the GA algorithm and try to improve it.
* Do some profiling tests to the simulation code

### 20171009
#### Done:
* multiprocessing library implemented successfully. 
* modified the code so that it runs on ozzy.
* Sorting of fitness array now returns the indexes not the sorted array, making life easier.
* New branch: ozzy-branch. This branch will host the version that runs on ozzy. Must be parallel and without any plotting.

#### To do:
* Fix code structure. The shared arrays force the code for the CA and the GA to be on the same file, then a restructure is needed.
* Test all different configurations: serial/parallel, optimised/not optimised.
* Separate the ploting code completely from the GA/CA.
* Ozzy version must write more information as csv files with good and descriptive names.

### 20171101
#### Done:
* Testing different parameters: number of processors, number of individuals, chunk sizes, number of generations.
* Script to run the different tests. To do this the main\_GA was modified to accept command line arguments.
* Now working on two different versions on two branches: the production branch is "ozzy-branch" and doesn't do any plotting at all, master branch is for plotting and do some minor testing that doesn't need much computational power.
* Saving data as csv files.
* gnuplot script to get some quick plots of the generated data.
* Fixed fitness function. Now it's possible to get a fitness of 1.
* Fixed the compass. V[5] -> V[7].
* Data for chemicals map. To see steady states and so on, a la dynamical systems.

#### To do:
* Use a database or pickle module to store the data in a systematic way.
* Test a different approach for parallelization: run GAs in parallel and maybe implement multithreading to evaluate individuals.
* Do a major cleaning of code.
* Implement the NEAT algorithm (?).
* Implement death cells.
* Use the try, except, finally statements. Learn about useful exceptions.

### 20171110
#### Done:
* Changed the way in which files are stored. Each run has a unique ID based on current time and all the generated files are asociated according to this ID. Parameter settings, population file names, and benchmarks are stored automatically.
* Fixed number of runs (specified as positional argument passed to the script) for every setting is executed now whitin main\_GA. This means that al the stistics stored are averaged over the amount of runs. Mentioned statistics are for now: max fitness and average fitness for every generation, benchmarks for each generation and for the total GA run.
* Fixed the way in which cells move. Using now try, except statements. Worth testing again.
* Adding new methods to plot.py. These methods will plot the generated data (GA statistics and benchmarks) using matplotlib.

#### To do:
* Fix, if it actually needs to be fixed, the network dynamics. Not sure if the current implementation is adequate for this problem. See Haykin.
* Get the required plots.
* Write the actual thesis document! Start by describing the model in detail.
* Fix the boundaries of the lattice. Some networks act as if the lattice was a torus!
* Investigate why initial individuals have a such a high fitness.

### 20171116
#### Done:
* Simulation runs in parallel using multiprocessing but in python 2.7. Had to drop `starmap` and now using `map` using a workaround to pass multiple arguments.
* New container for the cellgrid permits using the try except statements to keep the cells inbounds.

#### To do :
* Install anaconda with python 2.7 and try the optimization libraries (jit).
* Test the GA and in case is too fast there's no need to spawn multiple processes to run it. Do multiple runs in parallel instead.
* Try to use cython to make the simulation even faster.
* Finish the method for plotting the data!

### 20171215
#### Done:
* Many scripts to get plots from the networks.
* Scripts that generate graphs with some topology (as Erdõs-Rényi graphs) and then generate a network from them.
* Poster to present on the 9th Swedish Meeting on Mathematical Biology 201712-07/08, Västerås, Sweden.
* Read NEAT paper.
* Installed neat-python package.
* Script that runs neat-python using cell system as fitness function.
* Created a new branch to handle new code, scripts and modifications made in order to use neat-python.

#### To do:
* Test neat-python. Try to explore the parameter space to get ideal parameters for testing and production of the algorithm.
* Produce genomes in ozzy and visualise them on laptop.
* Play around with neat-python. See what interesting results could be obtained from it.
* Explore other implementations of NEAT.

---

## Recent Development (2024-2025)

### 2024-2025: Project Modernization and Web Interface
#### Done:
* **Project Restructuring**: Reorganized code into modular structure (core/, evolution/, visualization/, analysis/, examples/)
* **Documentation Improvements**: Enhanced README, added comprehensive docstrings, improved grammar and clarity
* **Containerization**: Implemented Docker support with Dockerfile, docker-compose.yml, and .dockerignore
* **Web Interface**: Created interactive Streamlit application with real-time visualization
* **Import Path Fixes**: Resolved all module import issues after restructuring
* **Dependencies Management**: Created requirements.txt with all necessary packages
* **Git Workflow**: Implemented proper branching strategy (master → main, feature branches)

#### Key Features Added:
* **Interactive Web Interface**: Real-time simulation control via Streamlit
* **Containerized Deployment**: Reproducible environments with Docker
* **Modular Architecture**: Clean separation of concerns across modules
* **Comprehensive Documentation**: Detailed explanations and usage examples
* **Modern Python Practices**: Updated import paths, dependency management

#### Technical Improvements:
* **Performance**: Optimized imports and module structure
* **Usability**: Web interface makes simulation accessible to non-programmers
* **Reproducibility**: Docker ensures consistent environments
* **Maintainability**: Modular structure improves code organization
* **Documentation**: Comprehensive guides and examples
