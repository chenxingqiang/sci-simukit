#!/usr/bin/env python3
"""
PRL (Physical Review Letters) Style Configuration for Figures

Provides consistent styling across all analysis scripts.
"""

import matplotlib.pyplot as plt

# PRL Style Configuration
PRL_RCPARAMS = {
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.minor.width': 0.4,
    'ytick.minor.width': 0.4,
    'lines.linewidth': 1.2,
    'lines.markersize': 6,
    'axes.grid': False,
    'axes.spines.top': True,
    'axes.spines.right': True,
}

# Color palette - professional and accessible
COLORS = {
    'pristine': '#1f77b4',  # Blue
    'B': '#d62728',         # Red
    'N': '#2ca02c',         # Green
    'P': '#9467bd',         # Purple
    'B+N': '#ff7f0e',       # Orange
}

MARKERS = {
    'pristine': 'o',
    'B': 's',
    'N': '^',
    'P': 'D',
    'B+N': 'p',
}


def apply_prl_style():
    """Apply PRL style to matplotlib."""
    plt.rcParams.update(PRL_RCPARAMS)


def get_color(dopant: str) -> str:
    """Get color for dopant type."""
    return COLORS.get(dopant, '#7f7f7f')


def get_marker(dopant: str) -> str:
    """Get marker for dopant type."""
    return MARKERS.get(dopant, 'o')

