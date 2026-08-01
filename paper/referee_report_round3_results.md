# PRB Simulated Referee Report — Round 3: Results (Section III)

**Date:** 2026-08-01  
**Manuscript:** *Non-Additive Strain–Doping Coupling in Quasi-Hexagonal C₆₀ Graphullerene*  
**Scope:** Section III, Figs. 1–4, Tables III–VIII (as cited in Results)

## Overall scores (referee rubric)

| Category               | Before | After revision (target) |
| ---------------------- | -----: | ------------------------: |
| Data quality           |    9.0 |                       9.0 |
| Physics interpretation |    8.5 |                       8.5 |
| Figure design          |    7.0 |                       8.0 |
| Logical progression    |    7.5 |                       8.5 |
| Statistical evidence   |    6.5 |                       7.5 |
| Reviewer resistance    |    7.0 |                       8.0 |

**Recommendation:** Major Revision → **borderline accept** after presentation fixes.

## Major comments — implementation status

### M1 — Figure 1 overloaded
- **Issue:** Four distinct messages in one figure.
- **Action:** Caption + Results text separate structure/landscape (Fig. 1) from synergy audit (Fig. 2). Full panel split (DOS/gap → new figure) **deferred** (layout change).

### M2 — Figure roadmap paragraph
- **Action:** Removed opening “Fig. X claim: …” block; replaced with protocol-scoped opener.

### M3 — Electronic structure mixes Discussion
- **Action:** Sec. IIIA reports DOS, gap, mechanical path only; bilinear/Taylor interpretation remains in Discussion.

### M4 — Unquantified “does not predict”
- **Action:** Removed from Results; Discussion uses “consistent with” + explicit absence of regression at $n=3$.

### M5 — $\alpha$ error bars; $n=3$ statistics
- **Action:** Fig. 3(d) horizontal bars = six-point linear-fit SE; Pearson/$R^2$/Spearman **removed** from figure and text.

### M6 — Central four-corner test not foregrounded
- **Action:** Subsection order: **Non-additive coupling first**; Fig. 2 caption leads with panel (c).

### M7 — Significance thresholds
- **Action:** Wording: **operational thresholds adopted in this work** (not universal 1%).

### M8 — Distribution panel
- **Action:** Fig. 2(d) histogram + inset box plot (median, Q1, Q3).

### M9 — Single P relaxation example
- **Action:** Results labels panel (e) **illustrative**; extension not audited.

### M10 — Interpretation in Results
- **Action:** Observation-only Results; one-sentence P size-mismatch hook → Discussion.

## Editor-style summary

> The four-corner additive-vs-coupled comparison is convincing. Revision clarifies observation vs interpretation, removes unsupported $n=3$ correlation statistics, and foregrounds the main quantitative test. Remaining presentation debt: optional physical split of Fig. 1 electronic panels.

## Files touched

- `paper/strain_doped_graphullerene.tex` (Sec. III reorder + rewrite)
- `paper/tables/fig_main_{1,2,3}.tex` (captions)
- `paper/figures/fig_prb_four_main.py`, `_load_audit.py` (box plot, $\alpha$ SE, no Pearson)
- `paper/response_to_referees.md` (Round 3 ledger)
