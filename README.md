# 🚀 Strain-Tuned Heteroatom-Doped Graphullerene Networks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CP2K](https://img.shields.io/badge/CP2K-2025.2-green.svg)](https://www.cp2k.org/)

## 📖 Overview

This repository contains the complete implementation of our research on **"Strain-Tuned Heteroatom-Doped Graphullerene Networks: Engineering Quantum Transport Properties through Controlled Lattice Deformation"**.

We present a comprehensive computational framework combining:
- 🔬 First-principles DFT calculations (CP2K)
- 🤖 Graph Neural Networks for property prediction
- 🧪 High-throughput materials screening
- 📊 Multi-scale modeling approach

## 🎯 Key Innovations

- **300% Enhancement** in electron mobility through optimal strain-doping combinations
- **Tunable Band Gap** range: 1.2-2.4 eV via synergistic strain and heteroatom effects
- **Machine Learning** acceleration: R² > 0.95 for property predictions
- **Device Applications**: Flexible electronics, strain sensors, optoelectronics

## 📁 Project Structure

```
sci-simukit/
├── 📄 README.md                    # This file
├── 📜 LICENSE                      # MIT License
├── 📋 requirements.txt             # Python dependencies
├── 🎓 paper/                       # LaTeX manuscript and figures
│   ├── strain_doped_graphullerene.tex
│   ├── strain_graphullerene_50refs.bib
│   └── figures/                    # Paper figures
├── 🧬 graphullerene/               # Base structures and CP2K inputs
│   ├── *.xyz                       # Fullerene structures
│   └── *.inp                       # CP2K input templates
├── 🔧 src/                         # Core implementation
│   ├── strain_generator.py         # Strain structure generation
│   ├── doping_generator.py         # Heteroatom doping
│   ├── strain_doping_combiner.py   # Combined strain+doping
│   └── graphullerene_gnn.py       # Graph neural network model
├── 🔬 experiments/                 # Experimental workflows
│   ├── run_complete_experiment.py  # Full pipeline
│   └── fullerene_strain_search.py  # Literature search tool
├── 📊 data/                        # Generated structures and results
│   ├── strained_structures/
│   ├── doped_structures/
│   └── strain_doped_structures/
└── 📈 results/                     # Analysis and visualizations
    ├── figures/
    └── reports/
```

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- CP2K 2025.2 (for DFT calculations)
- CUDA-capable GPU (optional, for ML training)

### Setup Environment

```bash
# Clone the repository
git clone https://github.com/chenxingqiang/graphullerene-strain-engineering.git
cd graphullerene-strain-engineering

# Create virtual environment
python3 -m venv fullerene-env
source fullerene-env/bin/activate  # On Windows: fullerene-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Generate Structures
```bash
# Generate strain structures
python src/strain_generator.py --strain_range -5 5 --strain_step 2.5

# Generate doped structures
python src/doping_generator.py --concentrations 2.5 5.0 7.5 --dopants B N P

# Generate combined strain+doping structures
python src/strain_doping_combiner.py --quick_test
```

### 2. Run Complete Experiment
```bash
# Quick test mode
python experiments/run_complete_experiment.py --mode quick

# Full production mode (requires HPC)
python experiments/run_complete_experiment.py --mode full
```

### 3. Train ML Model
```bash
python src/graphullerene_gnn.py
```

## 📊 Paper Figures and Tables

The paper requires the following figures and tables (see `paper/figures/` for outputs):

### Figures
1. **Fig. 1**: Graphullerene structure and strain/doping schemes
2. **Fig. 2**: Band structure evolution under strain
3. **Fig. 3**: Electron mobility vs. strain for different dopants
4. **Fig. 4**: ML model architecture and performance
5. **Fig. 5**: Phase diagram of optimal properties
6. **Fig. 6**: Device application schematics

### Tables
1. **Table 1**: Electronic properties of pristine and doped networks
2. **Table 2**: ML model performance metrics
3. **Table 3**: Comparison with experimental/literature values

## 💻 High-Performance Computing

For production DFT calculations on HPC clusters:

```bash
# Prepare batch job
sbatch hpc_scripts/run_cp2k_batch.sh

# Monitor progress
squeue -u $USER

# Collect results
python scripts/collect_hpc_results.py
```

## 📚 Citation

If you use this code in your research, please cite:

```bibtex
@article{chen2024strain,
  title={Strain-Tuned Heteroatom-Doped Graphullerene Networks: Engineering Quantum Transport Properties through Controlled Lattice Deformation},
  author={Chen, Xingqiang and Wang, Ying and Zhang, Ming and Li, Hao and Liu, Zhi and Zhang, Xue},
  journal={Nature Materials},
  year={2025},
  note={Submitted} 
}
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contact

- **Principal Investigator**: Prof. Xingqiang Chen
- **Email**: xingqiang.chen@university.edu
- **Lab Website**: https://graphullerene-lab.org

## 🙏 Acknowledgments

- CP2K developers for the excellent DFT software
- PyTorch Geometric team for graph neural network tools
- Funding agencies for computational resources

---

<p align="center">
Made with ❤️ by the Graphullerene Research Team
</p>
