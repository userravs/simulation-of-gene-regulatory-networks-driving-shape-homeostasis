# Web Interface Documentation

## Overview

The Gene Regulatory Network simulation includes an interactive web interface built with Streamlit and Plotly, providing real-time control and visualization of the simulation. This interface makes the complex simulation accessible to researchers, students, and anyone interested in exploring cellular automata and gene regulatory networks.

## Quick Start

### Prerequisites
- **Docker** (recommended) - No local Python installation needed
- **Python 3.7+** (for local development)

### Running the Web Interface

#### Option 1: Docker (Recommended)
```bash
# Start the containerized web application
./run_docker.sh

# Open your browser and go to: http://localhost:8501
```

#### Option 2: Local Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the web application
streamlit run web_app.py --server.port 8501 --server.address 0.0.0.0
```

## Interface Features

### 🎛️ Simulation Controls

The web interface provides three main tabs:

#### 1. Simulation Tab
- **Start/Pause/Reset Controls**: Real-time simulation control
- **Parameter Adjustment**: Modify simulation parameters in real-time
- **Live Visualization**: Watch the simulation evolve with interactive plots
- **Progress Tracking**: Monitor simulation progress and completion

#### 2. Analysis Tab
- **Fitness Analysis**: Generate and visualize fitness evolution over generations
- **Statistical Tools**: Analyze simulation results and performance
- **Data Export**: Save results for further analysis

#### 3. About Tab
- **Project Information**: Learn about the research and methodology
- **Technical Details**: Understand the underlying algorithms
- **Research Applications**: Explore potential use cases

### 📊 Parameter Controls

#### Simulation Parameters
- **Number of Nodes**: Size of the neural network (5-50, default: 25)
- **Lattice Size**: Size of the simulation grid (10-100, default: 50)
- **Time Steps**: Number of simulation steps (10-500, default: 100)

#### Network Architecture
- **Random**: Completely random network connections
- **Erdős-Rényi**: Random network with specified connection probability
- **Watts-Strogatz**: Small-world network with rewiring
- **Barabási-Albert**: Scale-free network with preferential attachment

### 🎨 Visualization Features

#### Real-time Plots
- **Cell States**: Visual representation of cell positions and states
- **SGF Concentration**: Short-range Growth Factor distribution
- **LGF Concentration**: Long-range Growth Factor distribution

![Simulation Visualization](../docs/images/cell_system_example.png)

*The web interface provides interactive versions of these visualizations with real-time controls.*

#### Interactive Elements
- **Zoom and Pan**: Explore different regions of the simulation
- **Color-coded States**: Easy identification of cell states
- **Dynamic Updates**: Real-time plot updates during simulation

## Technical Architecture

### Frontend
- **Streamlit**: Web framework for rapid application development
- **Plotly**: Interactive plotting library for real-time visualizations
- **Pandas**: Data manipulation and analysis

### Backend
- **Core Simulation**: Cellular automata and neural network engine
- **Evolutionary Algorithms**: Genetic algorithm for network optimization
- **Chemical Dynamics**: SGF and LGF diffusion equations

### Containerization
- **Docker**: Reproducible environment management
- **Port Mapping**: Web interface accessible on port 8501
- **Volume Mounting**: Data persistence and development support

## Usage Examples

### Basic Simulation
1. Open the web interface at http://localhost:8501
2. Navigate to the "Simulation" tab
3. Adjust parameters in the sidebar (optional)
4. Click "Start Simulation" to begin
5. Watch the real-time visualization
6. Use "Pause" or "Reset" as needed

### Parameter Exploration
1. Start with default parameters
2. Modify "Number of Nodes" to explore different network sizes
3. Change "Network Type" to test different architectures
4. Adjust "Time Steps" for longer/shorter simulations
5. Compare results across different configurations

### Fitness Analysis
1. Navigate to the "Analysis" tab
2. Click "Generate Fitness Analysis"
3. Examine the fitness evolution plot
4. Analyze performance trends and convergence

## Troubleshooting

### Common Issues

#### Web Interface Not Loading
- **Check Docker**: Ensure Docker is running
- **Verify Port**: Confirm port 8501 is not in use
- **Check Logs**: Review container logs for errors

#### Import Errors
- **Rebuild Container**: Run `docker-compose down && docker-compose up --build`
- **Check Dependencies**: Verify all packages are installed

#### Performance Issues
- **Reduce Parameters**: Lower lattice size or time steps
- **Close Other Applications**: Free up system resources
- **Use Local Installation**: For better performance on powerful machines

### Getting Help

1. **Check Documentation**: Review README.md and this guide
2. **Examine Logs**: Look at container logs for error messages
3. **Test Examples**: Try the provided example scripts
4. **Report Issues**: Create an issue on the project repository

## Advanced Usage

### Custom Network Architectures
The web interface supports different network types:
- **Random Networks**: Baseline for comparison
- **Small-world Networks**: Realistic biological network topology
- **Scale-free Networks**: Power-law degree distribution

### Data Export
- **CSV Export**: Save simulation data for external analysis
- **Plot Export**: Download visualizations as images
- **Parameter Logging**: Track simulation settings and results

### Integration with Research Workflow
- **Batch Processing**: Run multiple simulations with different parameters
- **Data Analysis**: Export results for statistical analysis
- **Collaboration**: Share reproducible environments via Docker

## Development

### Extending the Interface
- **New Visualizations**: Add custom plots using Plotly
- **Additional Parameters**: Extend the parameter controls
- **Custom Analysis**: Implement new analysis tools

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## References

- **Streamlit Documentation**: https://docs.streamlit.io/
- **Plotly Documentation**: https://plotly.com/python/
- **Docker Documentation**: https://docs.docker.com/
- **Cellular Automata**: https://en.wikipedia.org/wiki/Cellular_automaton
- **Gene Regulatory Networks**: https://en.wikipedia.org/wiki/Gene_regulatory_network
