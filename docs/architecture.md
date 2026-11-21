# Scientific Model and Software Architecture

## 1. Scientific Background and Thesis Objectives

This project implements the computational framework developed in the master's thesis **"Classification of Gene Regulatory Networks Driving Shape Homeostasis"** (*M.Sc. in Complex Adaptive Systems*) by **[M.Sc. José Esteban Pérez-Hidalgo](https://orion.tec.ac.cr/en/persons/jos%C3%A9-esteban-p%C3%A9rez-hidalgo/)** ([@j0sees](https://github.com/j0sees), [ORCID `0000-0001-7184-9974`](https://orcid.org/0000-0001-7184-9974), School of Physics, Costa Rica Institute of Technology; supervised by **[Ph.D. Philip Gerlee](https://research.chalmers.se/en/person/gerlee)**; [original `v0.1.0` baseline `6c3fae7`](https://github.com/j0sees/Simulation-of-Gene-Regulatory-Networks-Driving-Shape-Homeostasis/tree/6c3fae7834a2ca502b1a439d7535c4adab1673f3)), with software architecture, unified headless simulation engine (`core/engine.py`), $O(N^2)$ Thomas ADI reaction-diffusion solver (`LGFThomasSolver`), evolutionary diversity & NEAT upgrades, interactive phase-space/GRN inspector & vector overlays, accessible visualization, Podman/Docker containerization, and CI/test suite engineered and maintained by **Reymer Vargas** ([@userravs](https://github.com/userravs), [ORCID `0009-0002-9091-8431`](https://orcid.org/0009-0002-9091-8431), Independent Research Software Engineer, `v0.2.0`–`v0.4.0`). The model builds upon:

> Gerlee, P., Basanta, D., & Anderson, A. R. A. (2015). *The influence of cellular characteristics on the evolution of shape homeostasis*. Journal of the Royal Society Interface, 12(103), 20141222. [Chalmers Publication `251511`](https://research.chalmers.se/en/publication/251511) | [DOI: `10.1098/rsif.2014.1222`](https://doi.org/10.1098/rsif.2014.1222)

### Core Research Objectives
The thesis expands the Gerlee et al. framework to investigate how individual cellular capabilities—intracellular gene regulation, spatial polarization, and diffusible chemical signaling—give rise to self-organizing, homeostatic multicellular structures:

1. **Relaxing Network Constraints**: Replacing the constrained two-layer feedforward network of the original model with a fully connected **Recurrent Neural Network (RNN)** to explore a broader genotype and phenotype space.
2. **Enforcing Closed Spatial Boundaries**: Eliminating toroidal wrap-around artifacts at lattice borders so multicellular structures develop within bounded 2D domains.
3. **Behavioral Classification**: Demonstrating that evolved Gene Regulatory Networks (GRNs) that achieve shape homeostasis cluster into **three major behavioral classes**, defined by how cells balance proliferation, migration, quiescence, and apoptosis across environmental conditions.
4. **Graph Topology Exploration**: Evaluating how structural graph families (**Erdős-Rényi** random graphs, **Watts-Strogatz** small-world networks, and **Barabási-Albert** scale-free networks) influence homeostatic fitness and dynamical stability.

---

## 2. Mathematical Model

### Cellular Automata Lattice and Non-Toroidal Boundaries (`flatList`)
Cells inhabit a discrete 2D square lattice of size $N \times N$. At each discrete time step, every living cell is updated in random asynchronous order and adopts one of four behavioral states:

- **Quiet (`1`)**: Remains stationary at its current lattice site.
- **Move (`2`)**: Migrates to its preferred Von Neumann neighbor (if unoccupied), or to a random available Von Neumann neighbor.
- **Split (`3`)**: Divides and places a daughter cell with an identical genotype into its preferred (or another available) Von Neumann neighbor.
- **Die (`0`)**: Undergoes apoptosis and vacates its lattice site.

#### Closed Lattice Boundary Enforcement via `flatList`
In standard Python lists and NumPy arrays, negative indices (`grid[-1][x]`) wrap around to the opposite side of the array, causing the North and West lattice borders to behave like a **torus** while out-of-bounds positive indices (`grid[N][x]`) raise `IndexError`. To enforce **closed, non-toroidal boundaries** on all four borders without per-neighbor conditional branches, `core/tools.py` defines `flatList(list)`, which raises `IndexError` whenever `index < 0`. Both `Move()` and `Split()` catch `IndexError` to reject out-of-bounds neighbor coordinates uniformly on all four sides of the domain.

![Cell System Simulation](./images/cell_system_example.png)

*Simulation snapshot showing discrete cell states alongside Short-range Growth Factor (SGF) and Long-range Growth Factor (LGF) concentration fields.*

---

### Chemical Signaling (SGF and LGF) and Neumann Boundary Conditions
Intercellular communication is mediated by two chemical concentration fields over the lattice:

1. **Short-range Growth Factor (SGF, $s$)**: Produced locally at rate $\sigma$ and decays at rate $\delta_s$ without spatial diffusion:
   $$\frac{\partial s}{\partial t} = \sigma - \delta_s s$$
   Updated via explicit Euler discretization in `SGFDiffEq`:
   $$s(t + \Delta t) = s(t) + \Delta t \left(\sigma - \delta_s s(t)\right)$$

2. **Long-range Growth Factor (LGF, $l$)**: Produced locally at rate $\lambda$, decays at rate $\delta_l$, and diffuses across the lattice with diffusion constant $D$:
   $$\frac{\partial l}{\partial t} = D \nabla^2 l + \lambda - \delta_l l$$
   Integrated numerically in `core/tools.py` (`LGFThomasSolver` and `LGFDiffEq`) via an alternating-direction semi-implicit Crank-Nicolson (ADI) scheme using a precomputed Thomas tridiagonal factorization ($O(N^2)$ per time step) of $I - \frac{\alpha}{2}T$, where $T$ (`GenerateTMatrix`) is the discrete 1D Laplacian matrix:
   $$T = \begin{pmatrix} -1 & 1 & 0 & \cdots & 0 \\ 1 & -2 & 1 & \cdots & 0 \\ \vdots & \ddots & \ddots & \ddots & \vdots \\ 0 & \cdots & 1 & -2 & 1 \\ 0 & \cdots & 0 & 1 & -1 \end{pmatrix}$$
   Setting the corner entries $T_{0,0} = T_{N-1,N-1} = -1$ (instead of $-2$) enforces **zero-flux (homogeneous Neumann) boundary conditions** ($\nabla l \cdot \mathbf{n} = 0$) along the lattice perimeter so chemical factors do not leak out of the domain.

---

### Intracellular Gene Regulatory Network: From 2-Layer Feedforward to Recurrent Network

#### Original 2-Layer Feedforward Model (Gerlee et al., 2015)
In the original Gerlee et al. formulation, each cell's signaling network was restricted to a two-layer feedforward architecture with input-to-hidden weights $w$, hidden-to-output weights $W$, and threshold vectors $\theta$ and $\phi$:
$$V_j = \sigma\left(\beta \left(\sum_k w_{jk} I_k - \theta_j\right)\right), \qquad O_i = \sigma\left(\beta \left(\sum_j W_{ij} V_j - \phi_i\right)\right)$$
where $\sigma(x) = \frac{1}{1 + e^{-x}}$ and $\beta = 2$.

#### Generalized Recurrent Neural Network (RNN) in This Project
To allow arbitrary feedback loops, memory across time steps, and complex regulatory motifs, this project generalizes the intracellular controller into a single $n$-node **Recurrent Neural Network (`RecurrentNeuralNetwork`)** governed by a unified weight matrix $W \in [-1, 1]^{n \times n}$:
$$V_i(t + 1) = \frac{1}{1 + \exp\left(-2 \left(\sum_{j=0}^{n-1} W_{ij} V_j(t) - I_i(t)\right)\right)}$$

At each time step:
- **Inputs ($I$)**: Node `0` receives local SGF ($I_0 = s(y, x)$) and node `1` receives local LGF ($I_1 = l(y, x)$), with $I_k = 0$ for $k \ge 2$.
- **Action Selection (`V[2:5]`)**:
  - `V[2]` ($i_{\text{status}}$): Proliferation (`Split`)
  - `V[3]` ($j_{\text{status}}$): Migration (`Move`)
  - `V[4]` ($k_{\text{status}}$): Apoptosis (`Die`)
  - If all three activations are below the activation threshold $x_{\text{threshold}} = 0.5$, the cell remains **`Quiet`**. Otherwise, the action within $y_{\text{threshold}} = 0.01$ of the maximum activation $\max(V[2], V[3], V[4])$ is selected.
- **Chemical Secretion (`V[5:7]`)**:
  - `V[5]`: SGF production amount ($\sigma$)
  - `V[6]`: LGF production amount ($\lambda$)
- **Polarization Compass (`V[7]`)**:
  - Partitioned into four equal sub-intervals of $[0, 1]$ to set the cell's preferred Von Neumann neighbor: $[0, 0.25)$ North, $[0.25, 0.50)$ South, $[0.50, 0.75)$ East, and $[0.75, 1.0]$ West.

```mermaid
flowchart LR
    subgraph Inputs["Local Chemical Field (y, x)"]
        SGF_in["Node 0: SGF s(y, x)"]
        LGF_in["Node 1: LGF l(y, x)"]
    end

    subgraph GRN["Intracellular RNN (n x n Weight Matrix W)"]
        State["V(t+1) = sigmoid(2 * (W * V(t) - I(t)))"]
    end

    subgraph Outputs["Decoded Cellular Phenotype"]
        Act["V[2:5] -> Action Selection\nSplit (V[2]) | Move (V[3]) | Die (V[4])\nor Quiet if all < 0.5"]
        Sec["V[5:7] -> Chemical Secretion\nsigma_SGF (V[5]) | lambda_LGF (V[6])"]
        Comp["V[7] -> Polarization Compass\n[0, 0.25) N | [0.25, 0.5) S\n[0.5, 0.75) E | [0.75, 1.0] W"]
    end

    SGF_in --> State
    LGF_in --> State
    State -->|"Recurrent Memory V(t)"| State
    State --> Act
    State --> Sec
    State --> Comp
```

![Gene Regulatory Network](./images/network_example.png)

*Directed graph representation of a gene regulatory network with regulatory feedback loops.*

---

### Evolutionary Optimization and Behavioral Classes
To evolve networks that achieve **shape homeostasis** (a multicellular structure that self-organizes and maintains its spatial form over time), the genetic algorithm (`evolution/main_ga.py`) evaluates each candidate genotype over $T$ time steps and compares the binary cell occupancy matrix halfway through the simulation ($S_{T/2}$) against the final occupancy matrix ($S_T$):

$$F = 1 - \frac{1}{N^2} \sum_{i,j} \left|S_{T/2}(i, j) - S_T(i, j)\right|$$

Trivial or degenerate configurations—complete extinction, fewer than $1\%$ occupied lattice sites at $T/2$, or $100\%$ lattice saturation at $T$—are assigned $F = 0$.

```mermaid
flowchart LR
    Init["Initialize Population\n(P Weight Matrices W)"] --> Eval["Parallel Simulation\n(multiprocessing.Pool over T steps)"]
    Eval --> Fit["Compute Homeostasis Fitness\nF = 1 - (1/N^2) sum |S_{T/2} - S_T|"]
    Fit --> Check{"Generation\nLimit Reached?"}
    Check -->|"No"| Elite["Preserve Elite\n(Best Individual)"]
    Check -->|"No"| Tourn["Tournament Selection\n(p_tournament = 0.75)"]
    Tourn --> Recomb["Genetic Operators\nCrossover & Mutation / NEAT Speciation"]
    Elite --> NextGen["Next Generation Population"]
    Recomb --> NextGen
    NextGen --> Eval
    Check -->|"Yes"| Output["Export Best GRNs & Fitness History"]
```

![Evolutionary Progress](./images/evolution_example.png)

*Best and average population fitness across generations during evolutionary optimization.*

#### Dynamical Systems Phase-Space Maps (`MapPlot`)
To classify evolved GRNs into behavioral regimes, each network can be probed across a 2D grid of `(SGF, LGF)` input concentrations to record its steady-state cellular decision (`0..4`). The `MapPlot` utility in `visualization/plot.py` (and interactive `create_phase_space_plot` in `visualization/web_app.py`) renders these discrete decision regions across chemical concentration space, revealing the dynamical mechanism driving homeostasis.

![Phase-Space Map and Shape Homeostasis Comparison](./images/phase_space_example.png)

*Steady-state `(SGF, LGF)` cellular decision map (`Die`, `Quiet`, `Move`, `Split`) paired with midpoint occupancy ($S_{T/2}$), final occupancy ($S_T$), and structural delta ($|S_{T/2} - S_T|$).*

---

## 3. Software Architecture

### Platform Overview

```mermaid
flowchart LR
    subgraph Topologies["Graph Topologies (analysis/)"]
        ER["Erdos-Renyi"]
        WS["Watts-Strogatz"]
        BA["Barabasi-Albert"]
    end

    subgraph Engine["Headless Core Engine (core/engine.py)"]
        RNN["Intracellular RNN\n(RecurrentNeuralNetwork)"]
        CA["2D Cellular Automaton\n(Quiet, Move, Split, Die)"]
        PDE["Reaction-Diffusion PDEs\n(SGF Euler & LGFThomasSolver)"]
        RNN --> CA --> PDE --> RNN
    end

    subgraph Evolution["Evolutionary Optimization (evolution/)"]
        GA["Parallel Genetic Algorithm\n(main_ga.py, tools_ga.py)"]
        NEAT["NEAT Neuroevolution\n(neat_parallel.py)"]
    end

    subgraph UI["Visualization & Export (visualization/)"]
        Web["Streamlit & Plotly Web App\n(web_app.py)"]
        Plot["Matplotlib, Palettes & Timelapse\n(plot.py, palettes.py, timelapse.py)"]
    end

    Topologies --> Engine
    Evolution <-->|"Fitness F in [0, 1]"| Engine
    Engine -->|"StepSnapshot / SimulationResult"| UI
```

The codebase is organized into modular Python 3.11+ namespace packages:

| Directory / File | Responsibility |
|---|---|
| `core/engine.py` | Unified, plotting-free simulation stepper (`SimulationConfig`, `SimulationEngine`, `StepSnapshot`, `SimulationResult`, `run_simulation`) with deterministic PRNG seeding and $O(M)$ Fisher-Yates cell shuffling. |
| `core/cell_agent.py` | Defines the `cell` agent class (`Sense`, `GenerateStatus`, `Quiet`, `Move`, `Split`, `Die`) with `(y, x)` coordinates and injected RNG. |
| `core/tools.py` | Implements `flatList`, `(y, x)` grid helpers, Numba `@njit`-accelerated `SGFDiffEq`, precomputed $O(N^2)$ `LGFThomasSolver` / `LGFDiffEq`, `RecurrentNeuralNetwork`, and matrix utilities. |
| `core/main.py` | Headless simulation entrypoint and convenience API delegating directly to `core/engine.py`. |
| `evolution/main_ga.py` | Multiprocessing genetic algorithm (`run_ga`, `evaluate_genome`) delegating fitness evaluation to `core/engine.py`. |
| `evolution/tools_ga.py` | Genetic operators and population helpers (`Crossover`, per-gene `Mutate`, `initialize_population`, `select_tournament_parents`, `create_next_generation`, `DiracDelta`, `DifferentIndex`). |
| `evolution/neat_cell_agent.py` | Cell agent variant driven by a `neat-python` recurrent network genome. |
| `evolution/neat_parallel.py` | Parallel NEAT neuroevolution runner using `config/config-ca` and `SimulationEngine`. |
| `analysis/graph_generator.py` | Generates Erdős-Rényi, Watts-Strogatz, and Barabási-Albert graph ensembles for GRN topology studies. |
| `analysis/graph_evaluation.py` | Evaluates saved network populations in parallel via `core.engine.run_simulation` and plots fitness distributions. |
| `visualization/palettes.py` | Centralized Okabe-Ito colorblind-safe and legacy palettes plus discrete Plotly colorscales. |
| `visualization/timelapse.py` | Headless PNG snapshot rendering and animated GIF assembly (`TimelapseExporter`). |
| `visualization/plot.py` | Matplotlib `Environment` class, `make_live_plot_observer`, benchmark/fitness plots, and chemical phase-space `MapPlot`. |
| `visualization/web_app.py` | Interactive Streamlit and Plotly web interface powered by `SimulationEngine`, accessible palettes, vector overlays, phase-space/GRN inspectors, and GIF export. |
| `examples/` | Self-contained scripts (`run_simulation.py`, `run_evolution.py`, `generate_documentation_images.py`). |
| `tests/` | `pytest` unit test suite and golden numerical parity fixtures (`tests/fixtures/golden_parity_v0_2.json`). |

### Simulation Execution Flow

#### Coordinate Convention

All spatial indexing across `core/`, `evolution/`, and `visualization/` uses standardized row-major `(y, x)` ordering (`cell_grid[y][x]`, `chem_grid[y, x, channel]`, `CheckifOccupied(y, x, grid)`, and `CheckifPreferred(y_ori, x_ori, y, x)`). Within `cell`, compass directions map `North` to `y - 1`, `South` to `y + 1`, `East` to `x + 1`, and `West` to `x - 1`, rendered with `origin="lower"` in plots.

The diagram below illustrates the discrete time-step loop coupling asynchronous cellular updates with continuous SGF/LGF reaction-diffusion integration:

```mermaid
flowchart TD
    Start["Initialize N x N Lattice\ncell_grid (flatList), SGF=0, LGF=0\nPrecompute LGFThomasSolver (Neumann T)"] --> Seed["Seed Mother Cell at (y=N/2, x=N/2)"]
    Seed --> StepLoop["Time Step t = 0 .. T - 1"]
    StepLoop --> Async["Zero sigma_m, lambda_m\nDraw Living Cells in Random Asynchronous Order"]
    Async --> Sense["For Living Cell at (y, x):\n1. Sense(SGF[y,x], LGF[y,x])\n2. Update RNN State V(t+1)\n3. Decode Action & Compass"]
    Sense --> Secrete["Record Local Secretions Before Action:\nsigma_m[y,x] = V[5], lambda_m[y,x] = V[6]"]
    Secrete --> Action{"Selected Action"}
    Action -->|"1: Quiet"| Quiet["Remain at (y, x)"]
    Action -->|"2: Move"| Move["Migrate to Compass / Free Neighbor\n(flatList Rejects Out-of-Bounds)"]
    Action -->|"3: Split"| Split["Place Daughter Cell in Neighbor\n(flatList Rejects Out-of-Bounds)"]
    Action -->|"0: Die"| Die["Vacate Site (y, x)\nMark amidead = True"]
    Quiet --> Prune["Prune Dead Cells from cell_list"]
    Move --> Prune
    Split --> Prune
    Die --> Prune
    Prune --> PDE["Integrate Chemical Fields:\nSGF = SGFDiffEq(SGF, sigma_m)\nLGF = LGFThomasSolver.step(LGF, lambda_m) [O(N^2)]"]
    PDE --> MidCheck{"t == (T / 2) - 1 ?"}
    MidCheck -->|"Yes"| SaveMid["Check <= 1% Cutoff\nRecord Midpoint Occupancy Matrix S_{T/2}"]
    MidCheck -->|"No"| EndCheck{"t == T - 1 ?"}
    SaveMid --> EndCheck
    EndCheck -->|"No"| StepLoop
    EndCheck -->|"Yes"| Score["Check Saturation\nRecord S_T & Compute Fitness F in [0, 1]"]
```

---

## 4. References and Further Reading

1. **Pérez-Hidalgo, J. E.** (2017). *Classification of Gene Regulatory Networks Driving Shape Homeostasis*. M.Sc. Thesis in Complex Adaptive Systems, Department of Mathematical Sciences, University of Gothenburg & Chalmers University of Technology (supervised by [Ph.D. Philip Gerlee](https://research.chalmers.se/en/person/gerlee)).
2. **Gerlee, P., Basanta, D., & Anderson, A. R. A.** (2015). *The influence of cellular characteristics on the evolution of shape homeostasis*. Journal of the Royal Society Interface, 12(103), 20141222. ([Chalmers Publication `251511`](https://research.chalmers.se/en/publication/251511), [DOI: `10.1098/rsif.2014.1222`](https://doi.org/10.1098/rsif.2014.1222))
3. **Gerlee, P., Kim, E., & Anderson, A. R. A.** (2015). *Bridging scales in cancer progression: mapping genotype to phenotype using neural networks*. Seminars in Cancer Biology, 30, 30–41.
4. **Stanley, K. O., & Miikkulainen, R.** (2002). *Evolving Neural Networks through Augmenting Topologies*. Evolutionary Computation, 10(2), 99–127.
5. **Alon, U.** (2019). *An Introduction to Systems Biology: Design Principles of Biological Circuits* (2nd ed.). CRC Press.
6. **Murray, J. D.** (2003). *Mathematical Biology II: Spatial Models and Biomedical Applications* (3rd ed.). Springer.
7. **Deutsch, A., & Dormann, S.** (2017). *Cellular Automaton Modeling of Biological Pattern Formation* (2nd ed.). Birkhäuser.
8. **Eiben, A. E., & Smith, J. E.** (2015). *Introduction to Evolutionary Computing* (2nd ed.). Springer.
