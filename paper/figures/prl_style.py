"""Backward-compatible shim — figures use Nature-family style."""
from nature_style import (
    COLORS, MARKERS, NATURE_DOUBLE_COL, NATURE_ONE_HALF_COL, NATURE_SINGLE_COL,
    add_reference_line, apply_nature_style, finalize_axes, get_color, get_marker,
    nature_legend, save_figure, style_axes,
)
PRL_SINGLE_COL = NATURE_SINGLE_COL
PRL_ONE_HALF_COL = NATURE_ONE_HALF_COL
PRL_DOUBLE_COL = NATURE_DOUBLE_COL
def apply_prl_style() -> None:
    apply_nature_style()
