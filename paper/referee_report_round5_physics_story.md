# Simulated PRB Referee Report — Round 5 (Physics Story Audit)

**Perspective:** Associate Editor + Referee #2 (theory condensed matter)  
**Date:** 2026-08-01  
**Recommendation:** Major Revision → Minor Revision (if physics story reframed)

## Core reframing

| Old narrative | New narrative |
|---------------|---------------|
| We propose $\mathcal{S}$ | Additive strain--dopant screening **fails** under constrained load |
| Four-corner coupling energy is the contribution | $\mathcal{S}$ is a **finite-difference estimator** of $\partial^2 E/\partial\epsilon\partial\delta$ |
| Relaxation suppresses $\mathcal{S}$ (limitation) | Near-zero relaxed $\mathcal{S}$ proves **elastic-work origin** |

## Author response summary

| ID | Action |
|----|--------|
| M1 | Abstract/Intro/Methods/Conclusions: $\gamma\neq 0$ + screening failure; $\mathcal{S}$ not new observable |
| M2 | General rule: non-additivity scales with frozen local elastic incompatibility |
| M3 | Mechanism hierarchy (misfit → charge → π-DOS) retained |
| M4 | Qualitative $|\mathcal{S}|$ vs $|\Delta r_{\mathrm{cov}}|$ at $n{=}1$ (B/N/P audit) |
| M5 | Relaxed-limit physics in Abstract, Results, Discussion |
| M6 | “Electronic structure responds rather than controls” |
| M7 | Fig. 2 panel (f): additive-screening workflow schematic |
| M8 | Eq. (mixed derivative) in `sdc_method_section.tex` |
| M9 | Error-budget table `tab_sigma_S` |
| M10 | Applicability paragraph (rigid substrate, soft bonding, pre-strain) |

## Files touched

- `paper/strain_doped_graphullerene.tex`
- `paper/sdc_method_section.tex`
- `paper/tables/tab_sigma_S_benchmark.tex`
- `paper/tables/fig_main_2.tex`
- `paper/figures/_style.py`, `fig_prb_four_main.py`
- `paper/response_to_referees.md`

## Backlog (honest; not in main-text numbers)

- Dense $k$, SCAN/r²SCAN spot checks, periodic $n{=}4$ P relax (Limitations / Table σ_S pending rows)
