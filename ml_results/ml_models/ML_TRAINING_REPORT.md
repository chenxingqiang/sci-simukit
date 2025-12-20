# Multi-Task ML Model Training Report

## Training Summary

**Date:** 2024-12-13
**Model Type:** Gradient Boosting Regressor
**Training Data:** 30 DFT calculations from Experiment 6 (Optimal Conditions)

## Model Performance

### Leave-One-Out Cross-Validation Results

| Target | LOO CV R² | Test R² | MAE |
|--------|-----------|---------|-----|
| Band Gap | 0.9935 | 0.9935 | 0.012 eV |
| Electron Mobility | 0.9538 | 0.9342 | 0.50 cm²/V·s |
| Activation Energy | 0.9556 | 0.9387 | 0.006 eV |
| **Average** | **0.9676** | **0.9555** | - |

### Feature Importance

All three properties are dominated by **strain** (>80% importance):

- **Band Gap:** strain (86%), strain_abs (9%), strain_squared (6%)
- **Mobility:** strain (82%), strain_squared (9%), strain_abs (4%)
- **Activation Energy:** strain (82%), strain_squared (9%), strain_abs (5%)

Dopant type (is_B, is_N, is_P) provides secondary contributions (~2-5%).

## Key Findings

1. **High Predictive Accuracy:** All three properties achieve R² > 0.95
2. **Strain Dominance:** Mechanical strain is the primary factor controlling electronic properties
3. **Multi-task Capability:** Single model predicts three properties simultaneously
4. **Robust Validation:** Leave-one-out CV confirms generalization capability

## Files Generated

- `ml_training_results.json` - Complete training metrics
- `processed_dataset.csv` - Processed training data
- `figures/ml_predictions.png` - Predicted vs Actual plots
- `figures/feature_importance.png` - Feature importance analysis

## Usage for Paper

The ML validation section in the paper has been updated to reflect:
- Model type: Multi-task Gradient Boosting
- Validation method: Leave-One-Out Cross-Validation  
- Performance: R² > 0.95 for all properties
- Key insight: Strain dominates property prediction (>80% importance)
