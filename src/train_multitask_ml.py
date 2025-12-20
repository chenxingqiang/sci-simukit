#!/usr/bin/env python3
"""
Multi-Task Machine Learning Model for Graphullerene Property Prediction

This script trains ML models to predict:
1. Band gap (eV)
2. Electron mobility (cm²/V·s)
3. Activation energy (eV)

Using DFT calculation results from experiments 1-6.

Author: Xingqiang Chen
Date: 2024
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold, LeaveOneOut
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.multioutput import MultiOutputRegressor
import warnings
warnings.filterwarnings('ignore')

# Try importing XGBoost
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("XGBoost not available, using GradientBoosting instead")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GraphullereneDataCollector:
    """Collect and unify DFT results from all experiments."""
    
    def __init__(self, experiments_dir: Path):
        self.experiments_dir = experiments_dir
        self.dopant_encoder = LabelEncoder()
        
    def load_all_experiments(self) -> pd.DataFrame:
        """Load data from all experiments and create unified dataset."""
        all_data = []
        
        # Experiment 1: Structure (strain only)
        exp1_data = self._load_exp1()
        all_data.extend(exp1_data)
        logger.info(f"Exp1: {len(exp1_data)} data points")
        
        # Experiment 2: Doping
        exp2_data = self._load_exp2()
        all_data.extend(exp2_data)
        logger.info(f"Exp2: {len(exp2_data)} data points")
        
        # Experiment 3: Electronic properties
        exp3_data = self._load_exp3()
        all_data.extend(exp3_data)
        logger.info(f"Exp3: {len(exp3_data)} data points")
        
        # Experiment 4: Polaron
        exp4_data = self._load_exp4()
        all_data.extend(exp4_data)
        logger.info(f"Exp4: {len(exp4_data)} data points")
        
        # Experiment 5: Synergy
        exp5_data = self._load_exp5()
        all_data.extend(exp5_data)
        logger.info(f"Exp5: {len(exp5_data)} data points")
        
        # Experiment 6: Optimal conditions
        exp6_data = self._load_exp6()
        all_data.extend(exp6_data)
        logger.info(f"Exp6: {len(exp6_data)} data points")
        
        df = pd.DataFrame(all_data)
        logger.info(f"Total: {len(df)} data points")
        
        return df
    
    def _load_exp1(self) -> list:
        """Load Experiment 1 data (structure/strain)."""
        data = []
        json_file = self.experiments_dir / "exp_1_structure" / "results" / "dft_results.json"
        
        if not json_file.exists():
            return data
            
        with open(json_file) as f:
            results = json.load(f)
        
        for key, val in results.items():
            if val.get('status') == 'success':
                data.append({
                    'strain': val.get('strain', 0.0),
                    'dopant': 'pristine',
                    'concentration': 0.0,
                    'n_atoms': val.get('n_atoms', 120),
                    'total_energy': val.get('total_energy'),
                    'bandgap': None,
                    'mobility': None,
                    'activation_energy': None,
                    'experiment': 'exp1'
                })
        return data
    
    def _load_exp2(self) -> list:
        """Load Experiment 2 data (doping)."""
        data = []
        json_file = self.experiments_dir / "exp_2_doping" / "results" / "dft_results.json"
        
        if not json_file.exists():
            return data
            
        with open(json_file) as f:
            results = json.load(f)
        
        for key, val in results.items():
            if val.get('status') == 'success':
                dopant = val.get('dopant', 'pristine')
                data.append({
                    'strain': 0.0,
                    'dopant': dopant,
                    'concentration': val.get('concentration', 0.05),
                    'n_atoms': val.get('n_atoms', 60),
                    'total_energy': val.get('total_energy'),
                    'bandgap': val.get('bandgap'),
                    'mobility': None,
                    'activation_energy': None,
                    'experiment': 'exp2'
                })
        return data
    
    def _load_exp3(self) -> list:
        """Load Experiment 3 data (electronic properties)."""
        data = []
        json_file = self.experiments_dir / "exp_3_electronic" / "results" / "dft_results.json"
        
        if not json_file.exists():
            return data
            
        with open(json_file) as f:
            results = json.load(f)
        
        for key, val in results.items():
            if val.get('status') == 'success':
                data.append({
                    'strain': val.get('strain', 0.0),
                    'dopant': val.get('dopant', 'pristine'),
                    'concentration': 0.05,
                    'n_atoms': val.get('n_atoms', 120),
                    'total_energy': val.get('total_energy'),
                    'bandgap': val.get('bandgap'),
                    'mobility': val.get('mobility'),
                    'activation_energy': None,
                    'experiment': 'exp3'
                })
        return data
    
    def _load_exp4(self) -> list:
        """Load Experiment 4 data (polaron)."""
        data = []
        json_file = self.experiments_dir / "exp_4_polaron" / "results" / "dft_results.json"
        
        if not json_file.exists():
            return data
            
        with open(json_file) as f:
            results = json.load(f)
        
        for key, val in results.items():
            if val.get('status') == 'success':
                # Convert polaron_binding_energy from meV to eV if present
                polaron_be = val.get('polaron_binding_energy')
                if polaron_be is not None and polaron_be > 1:  # Likely in meV
                    polaron_be = polaron_be / 1000.0  # Convert to eV
                
                data.append({
                    'strain': val.get('strain', 0.0),
                    'dopant': val.get('dopant', 'pristine'),
                    'concentration': 0.05,
                    'n_atoms': val.get('n_atoms', 60),
                    'total_energy': val.get('total_energy'),
                    'bandgap': None,
                    'mobility': None,
                    'activation_energy': polaron_be,  # Now in eV
                    'ipr': val.get('ipr'),
                    'electronic_coupling': val.get('electronic_coupling'),
                    'experiment': 'exp4'
                })
        return data
    
    def _load_exp5(self) -> list:
        """Load Experiment 5 data (synergy)."""
        data = []
        json_file = self.experiments_dir / "exp_5_synergy" / "results" / "dft_results.json"
        
        if not json_file.exists():
            return data
            
        with open(json_file) as f:
            results = json.load(f)
        
        for key, val in results.items():
            if val.get('status') == 'success':
                data.append({
                    'strain': val.get('strain', 0.0),
                    'dopant': val.get('dopant', 'pristine'),
                    'concentration': 0.05,
                    'n_atoms': val.get('n_atoms', 60),
                    'total_energy': val.get('total_energy'),
                    'bandgap': None,
                    'mobility': None,
                    'activation_energy': None,
                    'ipr': val.get('ipr'),
                    'electronic_coupling': val.get('electronic_coupling'),
                    'reorganization_energy': val.get('reorganization_energy'),
                    'experiment': 'exp5'
                })
        return data
    
    def _load_exp6(self) -> list:
        """Load Experiment 6 data (optimal conditions)."""
        data = []
        json_file = self.experiments_dir / "exp_6_optimal" / "results" / "dft_results.json"
        
        if not json_file.exists():
            return data
            
        with open(json_file) as f:
            results = json.load(f)
        
        for key, val in results.items():
            if val.get('status') == 'success':
                data.append({
                    'strain': val.get('strain', 0.0),
                    'dopant': val.get('dopant', 'pristine'),
                    'concentration': 0.05,
                    'n_atoms': val.get('n_atoms', 60),
                    'total_energy': val.get('total_energy'),
                    'bandgap': val.get('bandgap'),
                    'mobility': val.get('mobility'),
                    'activation_energy': val.get('activation_energy'),
                    'experiment': 'exp6'
                })
        return data
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features and targets for ML training."""
        
        # Encode dopant type
        dopant_mapping = {
            'pristine': 0, 'B': 1, 'N': 2, 'P': 3, 
            'B+N': 4, 'Li': 5, 'Na': 6, 'K': 7
        }
        df['dopant_encoded'] = df['dopant'].map(dopant_mapping).fillna(0)
        
        # Create one-hot encoding for dopants
        df['is_B'] = (df['dopant'] == 'B').astype(int) | (df['dopant'] == 'B+N').astype(int)
        df['is_N'] = (df['dopant'] == 'N').astype(int) | (df['dopant'] == 'B+N').astype(int)
        df['is_P'] = (df['dopant'] == 'P').astype(int)
        df['is_pristine'] = (df['dopant'] == 'pristine').astype(int)
        df['is_mixed'] = (df['dopant'] == 'B+N').astype(int)
        
        # Feature columns
        feature_cols = ['strain', 'concentration', 'n_atoms', 
                       'is_B', 'is_N', 'is_P', 'is_pristine', 'is_mixed']
        
        # Add derived features
        df['strain_squared'] = df['strain'] ** 2
        df['strain_abs'] = df['strain'].abs()
        feature_cols.extend(['strain_squared', 'strain_abs'])
        
        X = df[feature_cols].values
        
        return X, df, feature_cols


class MultiTaskPropertyPredictor:
    """Multi-task ML model for property prediction."""
    
    def __init__(self, model_type='gradient_boosting'):
        self.model_type = model_type
        self.models = {}
        self.scalers = {}
        self.target_names = ['bandgap', 'mobility', 'activation_energy']
        self.r2_scores = {}
        self.mae_scores = {}
        
    def _create_model(self):
        """Create a single task model with regularization for small datasets."""
        if self.model_type == 'xgboost' and HAS_XGBOOST:
            return xgb.XGBRegressor(
                n_estimators=50,
                max_depth=3,
                learning_rate=0.05,
                reg_alpha=0.1,  # L1 regularization
                reg_lambda=1.0,  # L2 regularization
                random_state=42
            )
        elif self.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=50,
                max_depth=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        else:
            return GradientBoostingRegressor(
                n_estimators=50,
                max_depth=3,
                learning_rate=0.05,
                min_samples_leaf=2,
                random_state=42
            )
    
    def train(self, X: np.ndarray, df: pd.DataFrame, feature_names: list):
        """Train models for each target."""
        
        logger.info("=" * 60)
        logger.info("Training Multi-Task Property Prediction Models")
        logger.info("=" * 60)
        
        results = {}
        
        for target in self.target_names:
            # Filter rows with valid target values
            mask = df[target].notna()
            if mask.sum() < 10:
                logger.warning(f"Not enough data for {target}: {mask.sum()} samples")
                continue
            
            X_valid = X[mask]
            y_valid = df.loc[mask, target].values
            
            logger.info(f"\n{'='*40}")
            logger.info(f"Training model for: {target}")
            logger.info(f"Samples: {len(y_valid)}")
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_valid)
            self.scalers[target] = scaler
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_valid, test_size=0.2, random_state=42
            )
            
            # Create and train model
            model = self._create_model()
            model.fit(X_train, y_train)
            self.models[target] = model
            
            # Evaluate on test set
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            self.r2_scores[target] = r2
            self.mae_scores[target] = mae
            
            logger.info(f"Test R² Score: {r2:.4f}")
            logger.info(f"Test MAE: {mae:.4f}")
            logger.info(f"Test RMSE: {rmse:.4f}")
            
            # Leave-One-Out Cross-validation for small datasets
            loo = LeaveOneOut()
            y_pred_cv = np.zeros_like(y_valid)
            
            for train_idx, test_idx in loo.split(X_scaled):
                model_cv = self._create_model()
                model_cv.fit(X_scaled[train_idx], y_valid[train_idx])
                y_pred_cv[test_idx] = model_cv.predict(X_scaled[test_idx])
            
            cv_r2 = r2_score(y_valid, y_pred_cv)
            cv_mae = mean_absolute_error(y_valid, y_pred_cv)
            logger.info(f"LOO CV R² Score: {cv_r2:.4f}")
            logger.info(f"LOO CV MAE: {cv_mae:.4f}")
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': importance
                }).sort_values('importance', ascending=False)
                
                logger.info(f"\nTop 5 features for {target}:")
                for _, row in importance_df.head(5).iterrows():
                    logger.info(f"  {row['feature']}: {row['importance']:.4f}")
            
            results[target] = {
                'r2': r2,
                'mae': mae,
                'rmse': rmse,
                'loo_cv_r2': cv_r2,
                'loo_cv_mae': cv_mae,
                'n_samples': len(y_valid)
            }
        
        return results
    
    def predict(self, X: np.ndarray, target: str):
        """Predict property for new data."""
        if target not in self.models:
            raise ValueError(f"No model trained for {target}")
        
        X_scaled = self.scalers[target].transform(X)
        return self.models[target].predict(X_scaled)
    
    def save_results(self, results: dict, save_path: Path):
        """Save training results to JSON."""
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {save_path}")
    
    def plot_predictions(self, X: np.ndarray, df: pd.DataFrame, save_dir: Path):
        """Generate prediction vs actual plots for each target."""
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Multi-Task ML Model: Predicted vs Actual Values', fontsize=14, fontweight='bold')
        
        colors = {'bandgap': '#2E86AB', 'mobility': '#A23B72', 'activation_energy': '#F18F01'}
        units = {'bandgap': 'eV', 'mobility': 'cm²/V·s', 'activation_energy': 'eV'}
        
        for idx, target in enumerate(self.target_names):
            ax = axes[idx]
            
            if target not in self.models:
                ax.text(0.5, 0.5, f'No model for {target}', ha='center', va='center')
                continue
            
            # Filter valid data
            mask = df[target].notna()
            X_valid = X[mask]
            y_actual = df.loc[mask, target].values
            
            # Get predictions
            X_scaled = self.scalers[target].transform(X_valid)
            y_pred = self.models[target].predict(X_scaled)
            
            # Plot
            ax.scatter(y_actual, y_pred, c=colors[target], alpha=0.7, s=60, edgecolors='white')
            
            # Perfect prediction line
            min_val = min(y_actual.min(), y_pred.min())
            max_val = max(y_actual.max(), y_pred.max())
            margin = (max_val - min_val) * 0.05
            ax.plot([min_val - margin, max_val + margin], [min_val - margin, max_val + margin], 
                   'k--', lw=1.5, label='Perfect prediction')
            
            # Metrics
            r2 = self.r2_scores.get(target, 0)
            mae = self.mae_scores.get(target, 0)
            
            ax.set_xlabel(f'Actual {target.replace("_", " ").title()} ({units[target]})', fontsize=11)
            ax.set_ylabel(f'Predicted ({units[target]})', fontsize=11)
            ax.set_title(f'{target.replace("_", " ").title()}\nR² = {r2:.4f}, MAE = {mae:.4f}', fontsize=12)
            ax.set_xlim(min_val - margin, max_val + margin)
            ax.set_ylim(min_val - margin, max_val + margin)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        fig_path = save_dir / 'ml_predictions.png'
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"Prediction plot saved to {fig_path}")
        
        return fig_path
    
    def plot_feature_importance(self, feature_names: list, save_dir: Path):
        """Generate feature importance plots."""
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Feature Importance for Property Prediction', fontsize=14, fontweight='bold')
        
        colors = {'bandgap': '#2E86AB', 'mobility': '#A23B72', 'activation_energy': '#F18F01'}
        
        for idx, target in enumerate(self.target_names):
            ax = axes[idx]
            
            if target not in self.models:
                ax.text(0.5, 0.5, f'No model for {target}', ha='center', va='center')
                continue
            
            model = self.models[target]
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                
                # Sort by importance
                sorted_idx = np.argsort(importance)[::-1]
                
                # Take top 8
                top_n = min(8, len(sorted_idx))
                top_idx = sorted_idx[:top_n]
                
                ax.barh(range(top_n), importance[top_idx], color=colors[target], alpha=0.8)
                ax.set_yticks(range(top_n))
                ax.set_yticklabels([feature_names[i] for i in top_idx], fontsize=10)
                ax.invert_yaxis()
                ax.set_xlabel('Importance', fontsize=11)
                ax.set_title(f'{target.replace("_", " ").title()}', fontsize=12)
                ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        # Save figure
        fig_path = save_dir / 'feature_importance.png'
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"Feature importance plot saved to {fig_path}")
        
        return fig_path


def load_exp6_only(experiments_dir: Path) -> pd.DataFrame:
    """Load only Experiment 6 data for consistent multi-task training."""
    data = []
    json_file = experiments_dir / "exp_6_optimal" / "results" / "dft_results.json"
    
    if not json_file.exists():
        return pd.DataFrame()
    
    with open(json_file) as f:
        results = json.load(f)
    
    for key, val in results.items():
        if val.get('status') == 'success':
            data.append({
                'strain': val.get('strain', 0.0),
                'dopant': val.get('dopant', 'pristine'),
                'concentration': 0.05,
                'n_atoms': val.get('n_atoms', 60),
                'total_energy': val.get('total_energy'),
                'bandgap': val.get('bandgap'),
                'mobility': val.get('mobility'),
                'activation_energy': val.get('activation_energy'),
                'experiment': 'exp6'
            })
    
    return pd.DataFrame(data)


def main():
    """Main training pipeline."""
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    experiments_dir = project_root / "experiments"
    results_dir = project_root / "results" / "ml_models"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("Graphullerene Property Prediction - ML Training")
    logger.info("=" * 60)
    
    # Use only Exp6 for consistent multi-task training (all 3 targets available)
    logger.info("Using Experiment 6 data only (consistent multi-task targets)")
    df = load_exp6_only(experiments_dir)
    
    if len(df) == 0:
        # Fallback to all experiments
        logger.info("Exp6 data not available, loading all experiments")
        collector = GraphullereneDataCollector(experiments_dir)
        df = collector.load_all_experiments()
    
    logger.info(f"\nDataset Summary:")
    logger.info(f"Total samples: {len(df)}")
    logger.info(f"Samples with bandgap: {df['bandgap'].notna().sum()}")
    logger.info(f"Samples with mobility: {df['mobility'].notna().sum()}")
    logger.info(f"Samples with activation_energy: {df['activation_energy'].notna().sum()}")
    
    # Prepare features using collector's method
    collector = GraphullereneDataCollector(experiments_dir)
    X, df_processed, feature_names = collector.prepare_features(df)
    
    logger.info(f"\nFeatures: {feature_names}")
    logger.info(f"Feature matrix shape: {X.shape}")
    
    # Train models
    predictor = MultiTaskPropertyPredictor(model_type='gradient_boosting')
    results = predictor.train(X, df_processed, feature_names)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING SUMMARY")
    logger.info("=" * 60)
    
    for target, metrics in results.items():
        logger.info(f"\n{target}:")
        logger.info(f"  Test R² Score: {metrics['r2']:.4f}")
        logger.info(f"  LOO CV R² Score: {metrics['loo_cv_r2']:.4f}")
        logger.info(f"  Test MAE: {metrics['mae']:.4f}")
        logger.info(f"  LOO CV MAE: {metrics['loo_cv_mae']:.4f}")
        logger.info(f"  Samples: {metrics['n_samples']}")
    
    # Calculate overall R²
    r2_values = [m['r2'] for m in results.values()]
    avg_r2 = np.mean(r2_values)
    logger.info(f"\nOverall Average R²: {avg_r2:.4f}")
    
    # Generate visualizations
    figures_dir = results_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    predictor.plot_predictions(X, df_processed, figures_dir)
    predictor.plot_feature_importance(feature_names, figures_dir)
    
    # Calculate average LOO CV R² for paper
    loo_cv_r2_values = [m['loo_cv_r2'] for m in results.values()]
    avg_loo_cv_r2 = np.mean(loo_cv_r2_values)
    logger.info(f"Average LOO CV R²: {avg_loo_cv_r2:.4f}")
    
    # Save results
    save_results = {
        'model_type': 'gradient_boosting',
        'total_samples': len(df),
        'feature_names': feature_names,
        'targets': results,
        'average_test_r2': avg_r2,
        'average_loo_cv_r2': avg_loo_cv_r2
    }
    
    results_file = results_dir / "ml_training_results.json"
    predictor.save_results(save_results, results_file)
    
    # Save processed dataset
    df_processed.to_csv(results_dir / "processed_dataset.csv", index=False)
    logger.info(f"Dataset saved to {results_dir / 'processed_dataset.csv'}")
    
    return results, avg_loo_cv_r2


if __name__ == "__main__":
    results, avg_r2 = main()
    print(f"\n{'='*60}")
    print(f"ML TRAINING COMPLETE")
    print(f"Average R² Score: {avg_r2:.4f}")
    print(f"{'='*60}")

