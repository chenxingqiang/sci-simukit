# Simulated PRB Referee Report — Round 2: Computational Methods

**Recommendation:** Major Revision (unchanged; bottleneck shifts from narrative to **evidence vs. meV/atom claims**).

**Overall methodology scores (reviewer):** Reproducibility 9/10; computational rigor 8/10; numerical validation 6.5/10; error analysis 7/10; physical BCs 8.5/10; attack resistance 6/10.

---

## Major comments (summary)

| ID | Issue | Reviewer ask | Author response (R414) |
|----|--------|--------------|------------------------|
| **M1** | PBE+D3 cancellation assumed | SCAN / r²SCAN four-corner spot-check ($n{=}1$ P, $+3$\%) | Demonstrated vdW ($\mathcal{S}_{\mathrm{vdW}}\approx 0.33$ meV/atom) and partial cutoff audit in **Table~\ref{tab:sigma_S}**; meta-GGA rows **pending** (no numbers without `.out`) |
| **M2** | $\Gamma$-only $k$ sampling | $\Gamma$ vs $2\times 2\times 1$ for $n{=}1$ B/N/P @ $+3$\% | Explicit caution on smallest $|\mathcal{S}|$; dense-$k$ row **pending** in Table~\ref{tab:sigma_S} |
| **M3** | $\sigma_{\mathcal{S}}\lesssim 2$ meV provenance | Benchmark table (SCF, cutoff, $k$, XC, total) | New **Table~\ref{tab:sigma_S}** with analytic propagation + audited partial rows |
| **M4** | Rigid / upper bound buried | “Mechanically constrained loading” in Abstract opening | Abstract opens with **Under mechanically constrained loading**; rigid upper bound in Methods BC paragraph |
| **M5** | Relaxation benchmark weak (only $n{=}1$ P periodic) | Add $n{=}4$ P fixed-cell relax | Listed as **targeted backlog** in Validation + Limitations; no fabricated retention ratio |
| **M6** | Force threshold | — | **No change** (reviewer accepted 0.015 eV/Å) |
| **M7** | $\mathcal{S}$ Methods over-defensive | Compress ~40%; move interpretation to Discussion/SI | `sdc_method_section.tex` reduced to Eqs. + $\eta$ + pointer to **S-tab:descriptor** |
| **M8** | Descriptor comparison table in main | Move to SI | `tab_descriptor_comparison.tex` → SI only |
| **M9** | Taylor / $c\epsilon x$ physics late | Move to Introduction | **Eq.~\eqref{eq:taylor_coupling}** in Intro; $\mathcal{S}$ framed as estimator in Methods |
| **M10** | $\eta$ | Keep | Retained **Eq.~\eqref{eq:additive_fraction}** |

## Minor comments

| ID | Issue | Action |
|----|--------|--------|
| **m1** | Methods ~7 pages → target ~4 | Compressed coupling subsection; literature/descriptor tables to SI |
| **m2** | Discussion material in Methods | Observability/uniqueness → `sec:interpretive` + SI Table S-tab:descriptor |
| **m3** | “Scope for PRB” | Already removed Round 1 |

## Reviewer “one-sentence” concern

> Central conclusions depend on whether meV/atom-scale coupling survives $k$-point, XC, and ionic-relaxation convergence.

**Honest status:** Partial audits (cutoff, D3, tetramer + $n{=}1$ P relax) are **A-level**; SCAN, dense-$k$, and $n{=}4$ P periodic relax remain **blocking** for full attack resistance.

## Acceptance probability (reviewer model)

| Stage | ~Accept |
|-------|--------|
| Current draft (post-R414 text) | ~65% (text honest; gaps explicit) |
| + $k$-mesh benchmark | 72% |
| + SCAN spot-check | 80% |
| + $n{=}4$ P relax | 86% |

## Next section (Round 3)

**Results** — anticipated focus: Fig. 2 ($\mathcal{S}$, $\eta$), Fig. 3 ($\alpha$ vs $|\mathcal{S}|$), Fig. 4 (mechanism path), and whether Results oversell rigid magnitudes.

---

*Archive note: Maps to Loop R414 Track B + Loop C Methods revision.*
