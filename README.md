# Gas Infrastructure Model

## CSEI's Gas Infrastructure Model

The Gas Infrastructure Model is a linear transmission network optimization model developed by the Copenhagen School of Energy Infrastructure (CSEI). The model is designed to analyze the operation and development of gas transmission infrastructure and can be extended to assess the transition towards dedicated hydrogen transmission networks or integrated gas-hydrogen systems.

The model combines Python-based data preparation and analysis workflows with optimization routines implemented using Gurobi. Input data management, scenario generation, model execution, and result processing are performed through Jupyter Notebooks, providing a transparent and flexible modelling environment.

## Contents

- Description
- Documentation
- Installation
  - Requirements
  - Python Packages
  - Gurobi
- Contributing
- Citing
- License

## Description

The Gas Infrastructure Model is a tool for evaluating the operation, utilization, and expansion of gas transmission networks under different market, policy, and infrastructure development scenarios. The model can represent natural gas systems, hydrogen transmission networks, or hybrid systems that support the gradual transition from natural gas to hydrogen.

The model supports the analysis of:

- Gas and hydrogen transmission infrastructure
- Network bottlenecks and congestion
- Infrastructure expansion planning
- Pipeline repurposing from natural gas to hydrogen
- Cross-border transmission capacities
- Storage integration
- Scenario-based infrastructure development pathways

Input data preparation is performed in Python through a collection of Jupyter Notebooks. These routines allow users to define network topologies, infrastructure assets, technical parameters, demand scenarios, and investment options.

The optimization framework is implemented using Gurobi and formulated as a mathematical optimization problem. Depending on the application, the model can be used for operational dispatch analysis, capacity expansion planning, or long-term infrastructure development studies. The optimization accounts for technical and economic constraints governing the transmission system while ensuring reliable supply throughout the network.

Following optimization, Python-based post-processing routines analyze model outputs and generate key performance indicators, infrastructure utilization metrics, cost assessments, and visualizations of network flows and investment decisions.

## Documentation

Detailed documentation of the model structure, input data requirements, and example applications is currently under development.

## Installation

### Requirements

The current version of the Gas Infrastructure Model requires:

- Python 3.12 (recommended)
- Gurobi Optimizer
- Jupyter Notebook or JupyterLab

### Python Packages

We recommend creating a dedicated virtual environment (e.g., using Anaconda). The following Python packages are required:

- numpy
- pandas
- -gurobipy
- matplotlib
- networkx
- scipy
- jupyter
- ipywidgets
- os
- pathlib
- datetime
- pickle
- json
- requests

Additional packages may be required depending on the specific application and analysis modules.

### Gurobi

The optimization model relies on the Gurobi Optimizer. Please follow the official installation instructions and ensure that a valid Gurobi license is available:

https://www.gurobi.com/

## Contributing

The Gas Infrastructure Model is developed by the following people.

| Person | Contribution |
|----------|-------------|
| Johannes Giehl | Major development, conceptualization, model architecture, and data collection |
| Flora von Mikulicz-Radecki | Model development, methodology development |
| Mathilde Roger | Model development, data collection, result analysis routines |
| Kacper Rokosz | Input data routines |
| Mariana Pessoa | Data collection |

## Citing

We are currently working on a publication to introduce and apply the Gas Infrastructure Model.

For the current use of the model, please cite:

> Giehl, J., von Mikulicz-Radecki, F., Roger, M., Rokosz, K., and Pessoa, M. (2026): *The Gas Infrastructure Model*. Copenhagen School of Energy Infrastructure (CSEI), https://github.com/[repository-name], accessed YYYY-MM-DD.

## License

The Gas Infrastructure Model is licensed under the GNU Lesser General Public License version 3.0 or later.
