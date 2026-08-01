# Referee Report for Physical Review B (Strict Standard, Major Revision)

**Manuscript:** *Non-additive Strain–Dopant Energetics in Quasi-Hexagonal C₆₀ Graphullerene*  
**Authors:** Xingqiang Chen, Qixing Wang  
**Archive date:** 2026-08-01  
**Response ledger:** `paper/response_to_referees.md` (Round 7)

## Summary

PBE+D3 CP2K study of bilinear strain–doping coupling in qHP C₆₀ via four-corner finite-difference metric $\mathcal{S}$. Core value: exposing failure of additive high-throughput DFT screening under rigid lattice loading; P shows largest $|\mathcal{S}|$ (31.9 meV/atom at $n{=}1$). Rigid vs relaxed benchmarks support elastic-work dominance under constraint.

## Recommendation

**Major Revision** — mandatory new convergence/functional benchmarks, mechanistic decomposition, and text restructuring before re-review.

## Mandatory themes (ordered by severity)

1. **Convergence (fatal):** dense $k$-grid four-corner $\mathcal{S}$ for $n{=}1$ B/N/P; matched cutoff audit for $n{=}1$ P; SCAN benchmark; vdW cross-term audits beyond tetramer P.
2. **Metric definition:** finite-strain truncation at +3%; operational vs statistical thresholds for additive failure.
3. **Mechanism:** elastic vs electronic energy partition (Mayer/Bader/virial); N anomaly vs $\Delta r_{\mathrm{cov}}$ scaling; $\alpha$–$|\mathcal{S}|$ with $n{=}3$ species only.
4. **Boundary conditions:** rigid vs equilibrium regimes; $n{=}1$ PBC image effects; $\mathcal{S}_\infty$ extrapolation.
5. **Generalizability:** second host benchmark; cluster-expansion literature positioning.
6. **Presentation:** unified $\sigma_{\mathcal{S}}$ budget; figure error bars; SI raw corner energies; periodic $n{=}4$ bond statistics; finite-$T$ discussion.

## Author response strategy (Round 7)

| Class | Action |
|-------|--------|
| **Track A (DFT)** | Dense $k$, SCAN, $n{=}1$ P cutoff, Mayer/Bader, multi-strain grid, second host — **queued**; no new numbers in main text until converged |
| **Track B (text)** | Soften exclusive/elastic-origin and transferability claims; expand rigid/equilibrium partition; CE contrast; operational $\eta$ caveat; $n{=}1$ image caveat; error-budget pending rows |
| **Data** | Data Availability cites machine-readable four-corner energy components in public release |

---

## Round 7b — Mathematical & physical logic audit (Referee #2, theory)

**Archive date:** 2026-08-01  
**Response ledger:** `paper/response_to_referees.md` (Round 7b table)

### Verdict

The computational protocol and data quality meet PRB expectations; the **primary theoretical gap** was insufficient separation of the continuum mixed derivative $\gamma\equiv\partial^2 E/\partial\epsilon\,\partial\delta$ from the **four-corner finite-difference estimator** $\mathcal{S}$, and missing derivation of why Eq.~\eqref{eq:four_corner} isolates the bilinear term.

### Mandatory themes (theory)

| Theme | Author response |
|-------|-----------------|
| Discrete $\delta$ vs Taylor expansion | Methods + SI: finite-difference interpretation of $E(\epsilon,\delta)$ on the stencil |
| Why four corners (not central/LS/Hessian) | Methods `\paragraph{Why a four-point stencil?}`; SI Sec.~\ref{S-sec:why_four} |
| Derivation $\mathcal{S}\approx\gamma\,\Delta\epsilon\,\Delta\delta$ | SI Sec.~\ref{S-sec:four_corner_deriv}; main Eq.~\eqref{eq:mixed_derivative} |
| $\gamma$ vs $\mathcal{S}$ language | Throughout: $\mathcal{S}$ *estimates* mixed response; $\gamma$ is intrinsic coefficient |
| Units / $\eta$ dimensionless | Methods `\paragraph{Units, symmetry, and gauge invariance}`; SI Sec.~\ref{S-sec:symmetry_gauge} |
| $\sigma_{\mathcal{S}}=2\sigma_e$ | Eqs.~\eqref{eq:sigma_propagation}; SI Sec.~\ref{S-sec:error_prop} |
| Clairaut symmetry / gauge invariance | SI Sec.~\ref{S-sec:symmetry_gauge} |
| Taylor validity limit (${\gtrsim}10$\% strain, phase transitions) | Limitations cross-ref |

### New SI material

**Supplemental Material, Sec.~I** (`si_appendix_finite_difference.tex`): Taylor expansion, four-corner cancellation, stencil alternatives, symmetry/gauge/units, error propagation (~1 page).

### Mathematical consistency (author self-audit after revision)

| Item | Pre | Post (target) |
|------|-----|---------------|
| Taylor framework | 8.5 | 9.0 |
| Mixed derivative link | 6.5 | 8.5 |
| Finite-difference rigor | 6.0 | 8.5 |
| Error propagation | 7.5 | 9.0 |
| Physical interpretation ($\gamma$ vs $\mathcal{S}$) | 8.5 | 9.0 |
| Mathematical completeness | 6.5 | 8.5 |
