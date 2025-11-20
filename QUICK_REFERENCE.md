# 🚀 Quick Reference Guide

## Essential Commands

### **Setup**
```bash
# Initial setup
python3 -m venv fullerene-env
source fullerene-env/bin/activate
pip install -r requirements.txt

# Verify installation
python -c "import torch; import ase; import pymatgen; print('✓ All dependencies installed')"
```

### **Structure Generation**
```bash
# Generate strain structures
python src/strain_generator.py --strain_range -5 5 --strain_step 2.5

# Generate doped structures
python src/doping_generator.py --concentrations 2.5 5.0 7.5 --dopants B N P

# Generate combined structures
python src/strain_doping_combiner.py --quick_test
python src/strain_doping_combiner.py --mode full  # Full production
```

### **DFT Calculations**
```bash
# Local test run
python experiments/dft_experiment_runner.py --mode test

# HPC submission
cd hpc_calculations
./submit_all.sh

# Collect results
python scripts/collect_hpc_results.py
```

### **Machine Learning**
```bash
# Train GNN model
python src/graphullerene_gnn.py

# Expected output: best_graphullerene_gnn.pth with R² > 0.95
```

### **Validation**
```bash
# Run comprehensive validation
python experiments/comprehensive_validation_framework.py

# Calculate key metrics
python experiments/key_values_calculator.py

# Generate validation report
python experiments/run_comprehensive_experiments.py
```

### **Paper Figures**
```bash
# Generate all figures
python paper/paper_figures_generator.py

# Generate PRL-style figures
python paper/prl_figure_generator.py

# Visualize structures
python src/structure_visualizer.py
python src/publication_quality_figures.py
```

### **Compile Paper**
```bash
cd paper
pdflatex strain_doped_graphullerene.tex
bibtex strain_doped_graphullerene
pdflatex strain_doped_graphullerene.tex
pdflatex strain_doped_graphullerene.tex
# Output: strain_doped_graphullerene.pdf
```

---

## Key File Locations

### **Critical Data Files**
```
Base Structure:       graphullerene/C60.xyz
Strained Structures:  data/strained_structures/
Doped Structures:     data/doped_structures/
Combined Structures:  data/strain_doped_structures/

DFT Results:          hpc_calculations/results/
Validation Results:   experiments/comprehensive_results/
Final Figures:        paper/figures/publication_quality/
```

### **Important Scripts**
```
Structure Gen:        src/strain_generator.py
                      src/doping_generator.py
                      src/strain_doping_combiner.py

DFT Execution:        experiments/dft_experiment_runner.py
                      hpc_calculations/submit_all.sh

ML Model:             src/graphullerene_gnn.py
Validation:           experiments/comprehensive_validation_framework.py
Analysis:             experiments/key_values_calculator.py
Visualization:        src/publication_quality_figures.py
```

### **Documentation**
```
Main README:          README.md
Organization:         REPOSITORY_ORGANIZATION.md
Workflow:             WORKFLOW_DIAGRAM.md
Usage:                docs/USAGE_GUIDE.md
Validation:           FINAL_100_PERCENT_VALIDATION_REPORT.md
```

---

## Common Operations

### **Check Validation Status**
```bash
# View comprehensive report
cat FINAL_100_PERCENT_VALIDATION_REPORT.md

# Check individual experiments
cat experiments/exp_1_structure/results/validation_metrics.json
cat experiments/exp_2_doping/results/validation_metrics.json
# ... etc for exp_3 to exp_6
```

### **Monitor HPC Jobs**
```bash
# Check job status (SLURM)
squeue -u $USER

# Check job status (PBS)
qstat -u $USER

# View job output
tail -f hpc_calculations/logs/*.log

# Cancel all jobs
scancel -u $USER  # SLURM
qdel all          # PBS
```

### **Analyze Results**
```bash
# Extract key metrics
python experiments/key_values_calculator.py

# View results
cat results/integrated_validation_results.json | python -m json.tool

# Generate analysis plots
python src/publication_quality_figures.py
```

### **Debugging**
```bash
# Check CP2K installation
cp2k.psmp --version

# Test simple calculation
cd test_dft
cp2k.psmp simple_c60_test.inp > simple_c60_test.out

# Check Python environment
python -c "import sys; print(sys.executable)"
pip list | grep -E "torch|ase|pymatgen"

# View recent logs
tail -100 experiments/dft_experiment_runner.log
tail -100 hpc_calculations/logs/latest.log
```

---

## Key Parameters Reference

### **Structure Parameters**
```python
# Pristine C60 lattice
a = 36.67 Å  # Lattice parameter a
b = 30.84 Å  # Lattice parameter b
c = 20.0 Å   # Vacuum spacing

# Strain range
strain_min = -5%   # Compressive
strain_max = +5%   # Tensile
strain_step = 2.5%

# Doping
concentrations = [2.5%, 5.0%, 7.5%]
dopants = ['B', 'N', 'P']
distribution = ['uniform', 'random']
```

### **DFT Parameters (CP2K)**
```
Functional:       PBE
Dispersion:       rVV10 (b=7.8)
Basis Set:        DZVP-MOLOPT-GTH
Energy Cutoff:    500 Ry
Relative Cutoff:  50 Ry
SCF Convergence:  1.0E-6
K-points:         Gamma-only
```

### **ML Model Parameters**
```python
# GNN Architecture
input_dim = 64
hidden_dim = 128
output_dim = 1

# Training
train_split = 0.8
learning_rate = 0.001
epochs = 500
batch_size = 32

# Performance target
R_squared = 0.95  # Minimum acceptable
```

### **Target Validation Metrics**
```
Band Gap:           1.2-2.4 eV
Electron Mobility:  5.2-21.4 cm²V⁻¹s⁻¹
Optimal Mobility:   21.4 cm²V⁻¹s⁻¹ (3% strain + 5% doping)
Activation Energy:  0.09 eV (optimal)
IPR Change:         45-50 → 25-30
Electronic Coupling: 75 → 135 meV
Synergy Factor:     8.75 (300% enhancement)
```

---

## Experiment Quick Guide

### **Experiment Overview**
| # | Name | System | Key Metrics |
|---|------|--------|-------------|
| 1 | Structure | 1×C60 | Lattice: a=36.67±0.5Å, b=30.84±0.3Å |
| 2 | Doping | 1×C60 | Concentration: 2.5/5.0/7.5% ±0.2% |
| 3 | Electronic | 1×C60 | Gap: 1.2-2.4eV, μ: 5.2-21.4 cm²V⁻¹s⁻¹ |
| 4 | Polaron | 2×C60 | IPR: 45→25, J: 75→135meV |
| 5 | Synergy | 4×C60 | f_total=8.75, 300% enhancement |
| 6 | Optimal | 3×C60 | μ_max=21.4 at 3%strain+5%doping |

### **Run Individual Experiments**
```bash
# Experiment 1: Structure characterization
python experiments/exp_1_structure/run_structure_validation.py

# Experiment 2: Doping synthesis
python experiments/exp_2_doping/run_doping_validation.py

# Experiment 3: Electronic properties
python experiments/exp_3_electronic/run_electronic_validation.py

# Experiments 4-6: Advanced multi-molecule
python experiments/exp_4_polaron/run_polaron_validation.py
python experiments/exp_5_synergy/run_synergy_validation.py
python experiments/exp_6_optimal/run_optimal_validation.py
```

---

## Troubleshooting

### **Problem: Structure generation fails**
```bash
# Check C60.xyz exists
ls -lh graphullerene/C60.xyz

# Verify ASE installation
python -c "from ase.io import read; atoms=read('graphullerene/C60.xyz'); print(f'✓ {len(atoms)} atoms loaded')"

# Check output directory permissions
mkdir -p data/strained_structures
chmod 755 data/strained_structures
```

### **Problem: CP2K calculation errors**
```bash
# Check CP2K executable
which cp2k.psmp
cp2k.psmp --version

# Verify input file syntax
cp2k.psmp --check-only test.inp

# Check common issues
grep -i "error\|warning" test.out

# Monitor memory usage
top -p $(pgrep cp2k)
```

### **Problem: ML training fails**
```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Check data files
ls -lh results/*.json
python -c "import json; print(json.load(open('results/validation.json')))"

# Reduce batch size if OOM
# Edit src/graphullerene_gnn.py: batch_size = 16
```

### **Problem: Figure generation fails**
```bash
# Check matplotlib backend
python -c "import matplotlib; print(matplotlib.get_backend())"

# Install additional dependencies
pip install pillow

# Check output directory
mkdir -p paper/figures/publication_quality
chmod 755 paper/figures/publication_quality
```

---

## Performance Benchmarks

### **Typical Execution Times**
```
Structure Generation:      ~5 minutes (all structures)
Single CP2K Calculation:   ~30-60 minutes (depends on system size)
Full HPC Batch:            ~8-12 hours (65 calculations, 32 cores each)
ML Model Training:         ~2-4 hours (GPU), ~12-24 hours (CPU)
Validation Framework:      ~30 minutes
Figure Generation:         ~10 minutes
Paper Compilation:         ~2 minutes
```

### **Resource Requirements**
```
Disk Space:         ~50 GB (including all results)
RAM (Structure):    ~4 GB
RAM (DFT):          ~32-64 GB per calculation
RAM (ML Training):  ~16 GB (GPU), ~32 GB (CPU)
GPU VRAM (ML):      ~8 GB (optional but recommended)
```

---

## Important Notes

### **⚠️ Before Running Full HPC Jobs**
1. Test with `--mode test` locally first
2. Verify CP2K installation and modules
3. Check disk space availability (>50 GB)
4. Ensure correct paths in HPC scripts
5. Submit 1-2 test jobs before full batch

### **⚠️ Data Management**
1. Always backup results before re-running
2. Original DFT outputs are large (~GB per calculation)
3. Compressed archives available: `static_calculation.tgz`, `graphullerene_hpc.tar.gz`
4. Key results stored in JSON format for quick access

### **⚠️ Multi-Molecule Systems**
1. Experiments 1-3: Single C60 (60 atoms)
2. Experiments 4-6: Multiple C60 (120-240 atoms)
3. Use `experiments/c60_coordinates.py` functions:
   - `get_multi_c60_coordinates(num_molecules)`
   - `get_supercell_dimensions(num_molecules)`

### **✅ Best Practices**
1. Always activate virtual environment before running scripts
2. Use `--quick_test` mode for initial validation
3. Monitor HPC job queues regularly
4. Keep validation reports updated
5. Document any modifications in git commits

---

## Git Workflow

### **Commit Changes**
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: new validation framework for experiment 5"

# Push to remote
git push origin main
```

### **Useful Git Commands**
```bash
# View status
git status

# View recent changes
git log --oneline -10

# Create branch for new feature
git checkout -b feature/new-dopant-element

# Merge changes
git checkout main
git merge feature/new-dopant-element
```

---

## Contact and Support

### **Documentation**
- Main README: `README.md`
- Full organization: `REPOSITORY_ORGANIZATION.md`
- Workflow diagram: `WORKFLOW_DIAGRAM.md`
- Usage guide: `docs/USAGE_GUIDE.md`

### **Support Resources**
- CP2K manual: https://manual.cp2k.org/
- ASE documentation: https://wiki.fysik.dtu.dk/ase/
- PyTorch Geometric: https://pytorch-geometric.readthedocs.io/

### **Project Contact**
- PI: Prof. Xingqiang Chen
- Email: xingqiang.chen@university.edu
- Lab: https://graphullerene-lab.org

---

## Quick Status Check

### **Run This for Complete Status**
```bash
# Check environment
echo "=== Environment ==="
which python
python --version
pip list | grep -E "torch|ase|pymatgen" | head -5

# Check structure files
echo -e "\n=== Structures ==="
find data -name "*.inp" | wc -l
echo "CP2K input files generated"

# Check validation
echo -e "\n=== Validation ==="
if [ -f "FINAL_100_PERCENT_VALIDATION_REPORT.md" ]; then
    echo "✓ Validation complete (100%)"
else
    echo "⚠ Validation pending"
fi

# Check paper
echo -e "\n=== Paper ==="
if [ -f "paper/strain_doped_graphullerene.pdf" ]; then
    ls -lh paper/strain_doped_graphullerene.pdf
    echo "✓ Paper compiled"
else
    echo "⚠ Paper compilation pending"
fi

# Check ML model
echo -e "\n=== ML Model ==="
if [ -f "best_graphullerene_gnn.pth" ]; then
    ls -lh best_graphullerene_gnn.pth
    echo "✓ Model trained"
else
    echo "⚠ Model training pending"
fi
```

---

*Quick Reference v1.0 - Last Updated: November 20, 2025*

