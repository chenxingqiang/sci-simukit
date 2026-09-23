"""VBM/CBM VMD isosurfaces + band-edge pi-DOS — size series n=2,4,6,8."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

FIG_DIR = Path(__file__).resolve().parent
_DFT = FIG_DIR.parent.parent / "dft_results"
if str(_DFT) not in sys.path:
  sys.path.insert(0, str(_DFT))
from export_xyz_files import write_xyz  # noqa: E402

sys.path.insert(0, str(FIG_DIR))

from _pdos import gaussian_dos, parse_pdos
from _style import COLOR_CBM, COLOR_TOTAL, COLOR_VBM, apply_si_style, style_axes


@dataclass
class SizePanel:
  """One supercell size row in the composite figure."""

  n: int
  vbm_png: Path
  cbm_png: Path
  vbm_is_orbital: bool = True
  cbm_is_orbital: bool = True
  dopant: str | None = None  # None = pristine; else B, N, or P
  # n=8: optional per-cage tiles in 2D grid (default 2 rows x 4 cols)
  vbm_tiles: list[Path] | None = None
  cbm_tiles: list[Path] | None = None
  tile_grid: tuple[int, int] = (2, 4)  # (nrow, ncol)


def parse_tile_grid(spec: str) -> tuple[int, int]:
  """Parse '2x4' or '4x2' into (nrow, ncol)."""
  spec = spec.strip().lower().replace("*", "x")
  if "x" not in spec:
    return (2, 4)
  a, b = spec.split("x", 1)
  return (int(a), int(b))


def split_c60_cages(coords: list) -> list[list]:
  per = 60
  if len(coords) % per != 0:
    raise ValueError(f"expected multiple of 60 atoms, got {len(coords)}")
  return [coords[i : i + per] for i in range(0, len(coords), per)]


def order_cages_for_grid(cages: list[list], nrow: int, ncol: int) -> list[list]:
  coms: list[tuple[float, float, int]] = []
  for i, cage in enumerate(cages):
    xs = np.array([p[1] for p in cage], dtype=float)
    ys = np.array([p[2] for p in cage], dtype=float)
    coms.append((float(ys.mean()), float(xs.mean()), i))
  coms.sort(key=lambda t: (round(t[0], 1), t[1]))
  ordered = [cages[i] for _, _, i in coms]
  need = nrow * ncol
  return ordered[:need]


def export_cage_xyzs(coords: list, out_dir: Path, *, nrow: int = 2, ncol: int = 4) -> list[Path]:
  out_dir.mkdir(parents=True, exist_ok=True)
  cages = order_cages_for_grid(split_c60_cages(coords), nrow, ncol)
  paths: list[Path] = []
  for k, cage in enumerate(cages):
    path = out_dir / f"cage{k}.xyz"
    write_xyz(cage, path, f"cage {k} ({nrow}x{ncol})")
    paths.append(path)
  return paths


def _dopant_caption(dopant: str | None) -> str:
  if not dopant:
    return "pristine"
  return f"{dopant}-doped"


def _periodic_supercell_caption(*, orbital: bool = False) -> str:
  return (
      r"periodic supercell (DFT coordinates; intra-cage bonds only; "
      r"nearest-neighbor cage centers $\sim 10\,\mathrm{\AA}$)"
  )


def _cpk_supercell_caption(*, mode: str = "cpk") -> str:
  base = (
      r"periodic supercell (CPK; DFT coordinates; intra-cage contacts only; "
      r"nearest-neighbor cage centers $\sim 10\,\mathrm{\AA}$)"
  )
  if mode == "cages":
    return base + r"; cages color-coded"
  return base


def _surface_supercell_caption(*, mode: str = "quicksurf", probe: str | None = None) -> str:
  engine = "QuickSurf" if "msms" not in mode and "surf" not in mode else (
      "MSMS" if "msms" in mode else "Surf"
  )
  probe_note = ""
  if probe and ("msms" in mode or "surf" in mode):
    probe_note = rf"; probe $={probe}\,\mathrm{{\AA}}$"
  base = (
      rf"periodic supercell ({engine} molecular surface{probe_note}; DFT coordinates; "
      r"nearest-neighbor cage centers $\sim 10\,\mathrm{\AA}$)"
  )
  if mode in ("quicksurf_cages", "msms_cages", "surf_cages", "auto"):
    return base + r"; uniform gray carbon cages, heteroatom element-colored"
  return base


def _figure_title(*, dopant: str | None = None, epsilon: str = r"0") -> str:
  cap = _dopant_caption(dopant)
  return rf"qHP $C_{{60}}$ graphullerene ($\varepsilon{{=}}{epsilon}\%$, {cap})"


def postprocess_surface_snapshot(
  img: Image.Image,
  *,
  bg_threshold: int = 32,
) -> Image.Image:
  """Tachyon MSMS renders on a black plate; lift background to white and boost vividness."""
  from PIL import ImageEnhance

  arr = np.asarray(img.convert("RGB"), dtype=np.float32)
  lum = arr.mean(axis=2)
  bg = lum < bg_threshold
  rgb = arr.copy()
  rgb[bg] = 255.0
  out = Image.fromarray(rgb.astype(np.uint8))
  out = ImageEnhance.Contrast(out).enhance(1.10)
  out = ImageEnhance.Color(out).enhance(1.15)
  out = ImageEnhance.Sharpness(out).enhance(1.08)
  return out


def trim_white_margins(img: Image.Image, *, threshold: int = 248, pad: int = 12) -> Image.Image:
  """Crop near-white borders so VMD panels fill the matplotlib axes."""
  arr = np.asarray(img.convert("RGB"))
  mask = np.any(arr < threshold, axis=2)
  if not mask.any():
    return img
  ys, xs = np.where(mask)
  y0, y1 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + pad + 1, arr.shape[0])
  x0, x1 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + pad + 1, arr.shape[1])
  return img.crop((x0, y0, x1, y1))


def _show_panel(ax, png: Path) -> None:
  ax.imshow(np.array(trim_white_margins(Image.open(png))), aspect="equal")
  ax.axis("off")


def _show_tile_grid(ax, tiles: list[Path], nrow: int, ncol: int) -> None:
  """Show 8 (or nrow*ncol) cage tiles in a 2D grid inside one axes."""
  ax.axis("off")
  imgs = [trim_white_margins(Image.open(p)) for p in tiles[: nrow * ncol]]
  while len(imgs) < nrow * ncol:
    imgs.append(Image.new("RGB", imgs[0].size if imgs else (100, 100), (255, 255, 255)))
  w = max(im.size[0] for im in imgs)
  h = max(im.size[1] for im in imgs)
  canvas = Image.new("RGB", (w * ncol, h * nrow), (255, 255, 255))
  for idx, im in enumerate(imgs):
    r, c = divmod(idx, ncol)
    im2 = im.resize((w, h), Image.Resampling.LANCZOS)
    canvas.paste(im2, (c * w, r * h))
  ax.imshow(np.array(canvas), aspect="equal")


def plot_band_edge_pdos(ax, pdos_path: Path, *, dopant: str | None = None) -> None:
  series = parse_pdos(pdos_path)
  grid = np.linspace(-2.2, 1.4, 500)
  dos = gaussian_dos(series.energy_ev, series.pi_weight, grid, sigma_ev=0.06)
  valence = grid <= 0
  conduction = grid >= 0
  ax.fill_between(grid, 0, dos, where=valence, color=COLOR_VBM, alpha=0.85, lw=0)
  ax.fill_between(grid, 0, dos, where=conduction, color=COLOR_CBM, alpha=0.85, lw=0)
  ax.plot(grid, dos, color=COLOR_TOTAL, lw=0.55, alpha=0.5)
  ax.axvline(0, color="#333333", lw=0.55)
  ymax = float(dos.max()) * 1.12
  ax.set_xlim(-2.0, 1.2)
  ax.set_ylim(0, ymax)
  ax.set_xlabel(r"energy (eV)")
  ax.set_ylabel(r"$\pi$-DOS (a.u.)")
  ax.text(-1.85, ymax * 0.88, "VBM", fontsize=7, color=COLOR_VBM, ha="left", va="top")
  ax.text(0.15, ymax * 0.88, "CBM", fontsize=7, color=COLOR_CBM, ha="left", va="top")
  occ = series.energy_ev <= 0
  homo = float(series.energy_ev[occ].max()) if np.any(occ) else 0.0
  unocc = series.energy_ev[~occ]
  lumo = float(unocc.min()) if len(unocc) else homo
  gap_ev = max(lumo - homo, 0.0)
  cap = _dopant_caption(dopant)
  ax.text(
    0.03,
    0.97,
    f"gap $\\approx$ {gap_ev:.2f} eV ($n{{=}}2$, {cap})",
    transform=ax.transAxes,
    fontsize=6.5,
    va="top",
  )
  style_axes(ax)


def compose_size_scaling_vbm_figure(
  panels: list[SizePanel],
  pdos_path: Path,
  out_pdf: Path,
  *,
  title: str | None = None,
  dopant: str | None = None,
  supercell_caption=None,
) -> None:
  """Vertical layout: rows $n=2,4,6,8$ then $\pi$-DOS at bottom."""
  apply_si_style()
  if title is None:
    title = _figure_title(dopant=dopant or (panels[0].dopant if panels else None))
  panel_dop = dopant or (panels[0].dopant if panels else None)
  struct_cap = supercell_caption or _periodic_supercell_caption
  n_rows = len(panels)
  fig_h = 1.35 * n_rows + 2.2
  fig = plt.figure(figsize=(5.8, fig_h), dpi=300)
  height_ratios: list[float] = []
  for panel in panels:
    use_tiles_row = (
        panel.n == 8
        and panel.vbm_tiles
        and len(panel.vbm_tiles) >= 8
        and (
            (panel.cbm_tiles and len(panel.cbm_tiles) >= 8)
            or (not panel.vbm_is_orbital)
        )
    )
    height_ratios.append(1.25 if panel.n == 8 and not use_tiles_row else 1.0)
  height_ratios.append(0.72)
  gs = fig.add_gridspec(n_rows + 1, 2, height_ratios=height_ratios, hspace=0.28, wspace=0.08)

  for row, panel in enumerate(panels):
    d = panel.dopant or panel_dop
    dop_tag = f", {_dopant_caption(d)}" if d else ""
    row_title = rf"$n={panel.n}$ (${panel.n}\times C_{{60}}${dop_tag})"
    use_tiles = (
        panel.n == 8
        and panel.vbm_tiles
        and len(panel.vbm_tiles) >= 8
        and (
            (panel.cbm_tiles and len(panel.cbm_tiles) >= 8)
            or (not panel.vbm_is_orbital)
        )
    )
    nrow, ncol = panel.tile_grid
    grid_note = rf" ({nrow}$\times${ncol} cages)" if use_tiles else ""
    if use_tiles and not panel.vbm_is_orbital:
      ax = fig.add_subplot(gs[row, :])
      _show_tile_grid(ax, panel.vbm_tiles, nrow, ncol)
      ax.set_title(
        f"{row_title}{grid_note}\n{struct_cap()}",
        fontsize=8,
        fontweight="bold",
        color="#444444",
        pad=4,
      )
    elif use_tiles:
      for col, (tiles, label, color) in enumerate(
        [
          (panel.vbm_tiles, "VBM (HOMO)", COLOR_VBM),
          (panel.cbm_tiles, "CBM (LUMO)", COLOR_CBM),
        ]
      ):
        ax = fig.add_subplot(gs[row, col])
        _show_tile_grid(ax, tiles, nrow, ncol)
        ax.set_title(
          f"{row_title}{grid_note}\n{label}",
          fontsize=8,
          fontweight="bold",
          color=color,
          pad=3,
        )
    elif panel.vbm_is_orbital and panel.cbm_is_orbital:
      for col, (png, label, color) in enumerate(
        [(panel.vbm_png, "VBM (HOMO)", COLOR_VBM), (panel.cbm_png, "CBM (LUMO)", COLOR_CBM)]
      ):
        ax = fig.add_subplot(gs[row, col])
        _show_panel(ax, png)
        ax.set_title(f"{row_title}\n{label}", fontsize=8, fontweight="bold", color=color, pad=3)
    else:
      ax = fig.add_subplot(gs[row, :])
      _show_panel(ax, panel.vbm_png)
      ax.set_title(
        f"{row_title}\n{struct_cap()}",
        fontsize=8,
        fontweight="bold",
        color="#444444",
        pad=4,
      )

  ax_d = fig.add_subplot(gs[n_rows, :])
  plot_band_edge_pdos(ax_d, pdos_path, dopant=panel_dop)
  fig.suptitle(title, fontsize=8, y=0.995, style="italic")
  out_pdf.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
  fig.savefig(out_pdf.with_suffix(".png"), bbox_inches="tight", facecolor="white", dpi=300)
  plt.close(fig)
  print(f"Wrote {out_pdf}")


def build_panel_from_line(line: str, cache_dir: Path) -> SizePanel:
  """Parse render-script panel line (standard or n=8 TILES mode)."""
  parts = line.strip().split("|")
  n = int(parts[0])
  if parts[1] == "TILES":
    tag, vm, cm = parts[2], parts[3], parts[4]
    layout = parse_tile_grid(parts[5] if len(parts) > 5 else "2x4")
    dop = parts[6] if len(parts) > 6 else None
    if vm == "struct":
      tiles = [cache_dir / f"{tag}_cage{i}_struct.png" for i in range(8)]
      return SizePanel(
        n=n,
        vbm_png=tiles[0],
        cbm_png=tiles[0],
        vbm_is_orbital=False,
        cbm_is_orbital=False,
        dopant=dop,
        vbm_tiles=tiles,
        cbm_tiles=None,
        tile_grid=layout,
      )
    vbm_tiles = [cache_dir / f"{tag}_cage{i}_vbm.png" for i in range(8)]
    cbm_tiles = [cache_dir / f"{tag}_cage{i}_cbm.png" for i in range(8)]
    return SizePanel(
      n=n,
      vbm_png=vbm_tiles[0],
      cbm_png=cbm_tiles[0],
      vbm_is_orbital=True,
      cbm_is_orbital=True,
      dopant=dop,
      vbm_tiles=vbm_tiles,
      cbm_tiles=cbm_tiles,
      tile_grid=layout,
    )
  if len(parts) >= 6:
    vbm, cbm, vm, cm, dop = parts[1], parts[2], parts[3], parts[4], parts[5]
  else:
    vbm, cbm, vm, cm = parts[1], parts[2], parts[3], parts[4]
    dop = None
  return SizePanel(
    n=n,
    vbm_png=Path(vbm),
    cbm_png=Path(cbm),
    vbm_is_orbital=(vm == "orbital"),
    cbm_is_orbital=(cm == "orbital"),
    dopant=dop,
  )


def compose_single_size_figure(
  panel: SizePanel,
  out_pdf: Path,
  *,
  title: str | None = None,
  include_pdos: bool = False,
  pdos_path: Path | None = None,
  supercell_caption=None,
) -> None:
  """One standalone figure per supercell size (optional bottom $\pi$-DOS for $n{=}2$)."""
  apply_si_style()
  if title is None:
    title = _figure_title(dopant=panel.dopant)
  dop_tag = f", {_dopant_caption(panel.dopant)}" if panel.dopant else ""
  row_title = rf"$n={panel.n}$ (${panel.n}\times C_{{60}}${dop_tag})"
  struct_cap = supercell_caption or _periodic_supercell_caption
  use_tiles = (
      panel.n == 8
      and panel.vbm_tiles
      and len(panel.vbm_tiles) >= 8
      and (
          (panel.cbm_tiles and len(panel.cbm_tiles) >= 8)
          or (not panel.vbm_is_orbital)
      )
  )
  nrow, ncol = panel.tile_grid
  grid_note = rf" ({nrow}$\times${ncol} cages)" if use_tiles else ""

  if include_pdos and pdos_path is not None:
    fig_h = 5.2 if use_tiles else (3.6 if panel.vbm_is_orbital else 3.2)
    fig = plt.figure(figsize=(5.8, fig_h), dpi=300)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15 if use_tiles else 1.0, 0.72], hspace=0.32, wspace=0.08)
    if use_tiles and not panel.vbm_is_orbital:
      ax = fig.add_subplot(gs[0, :])
      _show_tile_grid(ax, panel.vbm_tiles, nrow, ncol)
      ax.set_title(
        f"{row_title}{grid_note}\n{struct_cap()}",
        fontsize=8,
        fontweight="bold",
        color="#444444",
        pad=4,
      )
    elif use_tiles:
      for col, (tiles, label, color) in enumerate(
        [
          (panel.vbm_tiles, "VBM (HOMO)", COLOR_VBM),
          (panel.cbm_tiles, "CBM (LUMO)", COLOR_CBM),
        ]
      ):
        ax = fig.add_subplot(gs[0, col])
        _show_tile_grid(ax, tiles, nrow, ncol)
        ax.set_title(
          f"{label}{grid_note}",
          fontsize=8,
          fontweight="bold",
          color=color,
          pad=3,
        )
    elif panel.vbm_is_orbital and panel.cbm_is_orbital:
      for col, (png, label, color) in enumerate(
        [(panel.vbm_png, "VBM (HOMO)", COLOR_VBM), (panel.cbm_png, "CBM (LUMO)", COLOR_CBM)]
      ):
        ax = fig.add_subplot(gs[0, col])
        _show_panel(ax, png)
        ax.set_title(label, fontsize=9, fontweight="bold", color=color, pad=4)
    else:
      ax = fig.add_subplot(gs[0, :])
      _show_panel(ax, panel.vbm_png)
      ax.set_title(
        f"{row_title}\n{struct_cap()}",
        fontsize=8,
        fontweight="bold",
        color="#444444",
        pad=4,
      )
    ax_d = fig.add_subplot(gs[1, :])
    plot_band_edge_pdos(ax_d, pdos_path, dopant=panel.dopant)
  elif use_tiles and not panel.vbm_is_orbital:
    fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=300)
    _show_tile_grid(ax, panel.vbm_tiles, nrow, ncol)
    ax.set_title(
      f"{row_title}{grid_note}\n{struct_cap()}",
      fontsize=8,
      fontweight="bold",
      color="#444444",
      pad=4,
    )
  elif use_tiles:
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.2), dpi=300)
    for ax, tiles, label, color in zip(
      axes,
      [panel.vbm_tiles, panel.cbm_tiles],
      ["VBM (HOMO)", "CBM (LUMO)"],
      [COLOR_VBM, COLOR_CBM],
    ):
      _show_tile_grid(ax, tiles, nrow, ncol)
      ax.set_title(
        f"{label}{grid_note}",
        fontsize=8,
        fontweight="bold",
        color=color,
        pad=3,
      )
  elif panel.vbm_is_orbital and panel.cbm_is_orbital:
    fig, axes = plt.subplots(1, 2, figsize=(5.8, 2.5), dpi=300)
    for ax, png, label, color in zip(
      axes,
      [panel.vbm_png, panel.cbm_png],
      ["VBM (HOMO)", "CBM (LUMO)"],
      [COLOR_VBM, COLOR_CBM],
    ):
      _show_panel(ax, png)
      ax.set_title(label, fontsize=9, fontweight="bold", color=color, pad=4)
  else:
    fig, ax = plt.subplots(figsize=(5.2, 3.4), dpi=300)
    _show_panel(ax, panel.vbm_png)
    ax.set_title(
        f"{row_title}\n{struct_cap()}",
        fontsize=7.5,
        fontweight="bold",
        color="#444444",
        pad=4,
    )

  fig.suptitle(f"{title}\n{row_title}", fontsize=8, y=0.99, style="italic")
  out_pdf.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
  fig.savefig(out_pdf.with_suffix(".png"), bbox_inches="tight", facecolor="white", dpi=300)
  plt.close(fig)
  print(f"Wrote {out_pdf}")


def compose_vbm_cbm_figure(
  vbm_png: Path,
  cbm_png: Path,
  pdos_path: Path,
  out_pdf: Path,
  *,
  title: str = r"qHP $C_{60}$ graphullerene ($\varepsilon{=}0$, pristine)",
) -> None:
  """Backward-compatible single-$n$ wrapper."""
  compose_size_scaling_vbm_figure(
    [SizePanel(n=2, vbm_png=vbm_png, cbm_png=cbm_png)],
    pdos_path,
    out_pdf,
    title=title,
  )
