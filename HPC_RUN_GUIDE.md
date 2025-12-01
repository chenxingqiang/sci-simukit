# HPC Server Run Guide

## Quick Start

### 1. Copy Repository to Server

```bash
# Option A: Use scp
scp -r /Users/xingqiangchen/sci-simukit user@server:/path/to/destination/

# Option B: Use rsync (recommended for large repos)
rsync -avz --exclude='*.wfn*' --exclude='*.log' \
  /Users/xingqiangchen/sci-simukit/ user@server:/path/to/destination/
```

### 2. Server Environment Setup

```bash
# Load CP2K module (adjust based on your HPC system)
module load cp2k/2023.2

# Or if using conda
conda activate cp2k-env

# Verify CP2K
which cp2k.psmp  # or cp2k.popt for MPI version
```

### 3. Run Experiments

#### Experiment 1: Structure Analysis
```bash
cd /path/to/sci-simukit/experiments/exp_1_structure
python run_structure_experiment.py
```

#### Experiment 2: Doping Synthesis
```bash
cd /path/to/sci-simukit/experiments/exp_2_doping
python run_doping_experiment.py
```

#### Experiment 2: Polaron Binding Energy (New)
```bash
cd /path/to/sci-simukit/experiments/exp_2_doping
python calculate_polaron_binding.py
```

## HPC Batch Scripts

### PBS/Torque

```bash
#!/bin/bash
#PBS -N polaron_calc
#PBS -l nodes=1:ppn=16
#PBS -l walltime=24:00:00
#PBS -l mem=64gb

cd $PBS_O_WORKDIR
module load cp2k

python calculate_polaron_binding.py
```

### SLURM

```bash
#!/bin/bash
#SBATCH --job-name=polaron_calc
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=24:00:00
#SBATCH --mem=64G

cd $SLURM_SUBMIT_DIR
module load cp2k

python calculate_polaron_binding.py
```

## Key Files

| File | Description |
|------|-------------|
| `experiments/c60_coordinates.py` | C60 60-atom structure coordinates |
| `experiments/exp_2_doping/calculate_polaron_binding.py` | Polaron λ calculation |
| `experiments/exp_2_doping/run_doping_experiment.py` | Doping formation energy calculation |
| `experiments/exp_1_structure/run_structure_experiment.py` | Strain-structure analysis |

## Expected Results

### Polaron Binding Energy (λ)
- **Pristine C60**: λ_e = 0.10-0.13 eV
- **B-doped C60**: λ_e ~ 0.08-0.12 eV  
- **N-doped C60**: λ_e ~ 0.09-0.12 eV

### Doping Formation Energy (E_f)
- **B-doped**: ~31-50 eV (substitutional)
- **N-doped**: ~100-150 eV (substitutional)
- **P-doped**: ~300-460 eV (substitutional)

## Time Estimates

| Calculation | Local (M1) | HPC (16 cores) |
|-------------|------------|----------------|
| Single SCF | ~45 min | ~10 min |
| Geometry Opt | ~2-3 hrs | ~30-60 min |
| Full Polaron (1 system) | ~3-4 hrs | ~1-2 hrs |
| All Experiments | ~24 hrs | ~6-8 hrs |

## Troubleshooting

### CP2K Not Found
```bash
# Check available modules
module avail cp2k

# Or find CP2K
find /opt -name "cp2k*" 2>/dev/null
```

### Memory Issues
Edit `calculate_polaron_binding.py`:
```python
# Reduce cell size
CELL_SIZE = 20  # from 25

# Reduce CUTOFF
CUTOFF = 300  # from 400
```

### SCF Not Converging
Edit input files:
```
&SCF
  MAX_SCF 500      # Increase from 200
  EPS_SCF 1.0E-4   # Relax from 1.0E-5
&END SCF
```

## Monitor Progress

```bash
# Check running jobs (SLURM)
squeue -u $USER

# Check output
tail -f polaron_calculations/*.out

# Check SCF convergence
grep "Step.*Convergence" polaron_calculations/*.out | tail -10
```

## Results Location

After completion:
- `polaron_calculations/polaron_binding_*.json` - Polaron λ results
- `results/dft_results.json` - DFT calculation results
- `results/validation_report.json` - Validation summary

---

**Last Updated**: 2024-12-01  
**Commit**: 511dcc2

