# 🧬 Simulation of Gene Regulatory Networks Driving Shape Homeostasis

This repository contains the software developed as part of the master’s thesis

**“Classification of Gene Regulatory Networks Driving Shape Homeostasis”**  

by **M.Sc. J. Esteban Pérez-Hidalgo** (School of Physics, Costa Rica Institute of Technology), under the supervision of **PhD. Philip Gerlee** (Department of Mathematical Sciences, University of Gothenburg & Chalmers University of Technology, Sweden).

---

## 📌 Overview

This software allows the **simulation and classification of Gene Regulatory Networks (GRNs)** that drive **shape homeostasis** in multicellular systems — a key emergent phenomenon in developmental biology and artificial life.

The simulation is entirely written in **Python** and is based on the framework proposed by **Gerlee et al.** in the study _“The influence of cellular characteristics on the evolution of shape homeostasis”_, supported by several foundational models in the field of artificial life cited in the thesis.

---

## 🎯 Purpose

- To simulate multicellular collectives and observe adaptive behavior under dynamic environments.
- To classify GRNs that can maintain **shape homeostasis** in different environmental conditions.
- To explore the role of **growth factors**, **cell–cell interactions**, and **internal cellular actions** in emergent behavior.
- To demonstrate that **three major behavioral classes** lead to shape homeostasis.
- To showcase cellular responses as a function of different environmental types.

---

## 🧪 Methods and Technologies

This software combines a range of well-established computational techniques:

- 🔲 **Cellular Automata** — for modeling spatial environments and local cell dynamics.
- 🧠 **Artificial Neural Networks** — to implement gene regulatory networks within each cell.
- 🔍 **Optimization Algorithms** — to evolve adaptive networks and collective behavior.

These components interact to simulate the dynamics of cellular collectives, where behavior arises from:

- A dynamic equilibrium of cellular actions,
- The interaction between two growth factors enabling communication,
- And a signaling network acting as a **gene regulatory network**.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Dependencies listed in `requirements.txt`

### Installation

#### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/your-username/simulation-of-gene-regulatory-networks-driving-shape-homeostasis.git
cd simulation-of-gene-regulatory-networks-driving-shape-homeostasis

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/simulation-of-gene-regulatory-networks-driving-shape-homeostasis.git
cd simulation-of-gene-regulatory-networks-driving-shape-homeostasis

# Run with Docker (no local Python installation needed)
./run-docker.sh
```

### Basic Usage

#### With Docker (Recommended)

```bash
# Start the container
./run-docker.sh

# Inside the container, run:
python examples/run_simulation.py    # Basic simulation
python examples/run_evolution.py    # Genetic algorithm example
python evolution/main_GA.py         # Main GA application
python core/main.py                 # Visualization simulation
```

#### Local Installation

```bash
# Run a simple simulation example
python examples/run_simulation.py

# Run genetic algorithm example
python examples/run_evolution.py

# Run main applications directly
python core/main.py [filename] [nNodes] [individual]
python evolution/main_GA.py [filename] [parameters]
```

---

## 📁 Project Structure

```
├── core/                    # Core simulation components
│   ├── cell_agent.py        # Cell class and neural network
│   ├── main.py              # Basic simulation engine
│   └── tools.py             # Utility functions
├── evolution/               # Genetic algorithm
│   ├── main_GA.py           # Main GA application
│   └── tools_GA.py          # GA utilities
├── visualization/           # Plotting and visualization
│   └── plot.py              # Plotting functions
├── config/                  # Configuration files
│   └── config-ca            # NEAT configuration
├── analysis/                # Research tools
│   ├── graph_generator.py   # Network generation
│   └── graph_evaluation.py  # Network evaluation
├── examples/                # Usage examples
│   ├── run_simulation.py    # Basic simulation example
│   └── run_evolution.py     # GA example
└── requirements.txt         # Dependencies
```

---

## 🧬 Scientific Contribution

This software represents a **novel, multidisciplinary product**, combining:

- Computational Physics  
- Numerical Methods in Mathematics  
- Computational Biology  

It provides a computational platform for studying **emergent homeostasis**, offering insights into how multicellular systems organize and regulate their shape.

---

## 👨‍🏫 Autor

- M.Sc. J. Esteban Pérez-Hidalgo (School of Physics, Costa Rica Institute of Technology)
- Master's Thesis – University of Gothenburg & Chalmers University of Technology  
- Email: jose.perez@tec.ac.cr
