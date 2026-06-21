> **Loop C 索引**：`AGENTS.md` § PRB Report No. 1 — IDs **C-M1…C-M4**, **C-m1…C-m5**.

# Response to Referees — PRB Major Revision

**Manuscript:** Non-Additive Strain--Doping Coupling in Quasi-Hexagonal C$_{60}$ Graphullerene  
**Journal:** Physical Review B (Regular Article)

---

## Major Comment 1 — Rigid strain lacks relaxation validation

**Referee concern:** All $\alpha$ and $\mathcal{S}$ use fixed fractional coordinates; no relax benchmark; reported $|\mathcal{S}|$ may be an upper bound.

**Response:** We agree that fixed fractional coordinates can overestimate strain coupling and that equilibrium relevance must be demonstrated. We have (i) relabeled all main-text $|\mathcal{S}|$ magnitudes as **protocol upper bounds** at fixed coordinates (Abstract, Methods, Results, Discussion design language); (ii) **removed** the prior rhetorical contrast between the archived rigid tetramer Table~III entry ($\mathcal{S}=+0.96$~meV/atom) and periodic $n{=}4$ $P$ ($-23.7$~meV/atom), which the referee correctly notes is **not** a valid control because concentration and boundary conditions differ; and (iii) reframed **Table~III** as a **sign-qualitative** tetramer benchmark only: rigid references use legacy PBE (no D3) whereas relaxed corners use PBE+D3, so a quantitative $|\mathcal{S}_{\mathrm{relaxed}}|/|\mathcal{S}_{\mathrm{rigid}}|$ ratio is **not** claimed until a matched-functional rigid grid exists. Fixed-cell geometry optimization is **in progress** (2/4 corners converged: pristine $\epsilon{=}0$ and $+3$\%; $P@\epsilon{=}0$ in the inner-SCF critical zone, OT${\sim}85$, gradient ${\sim}1.6\times10^{-6}$~Ha/bohr). Marcus vertical SP (8/8) is complete; the relax queue continues without parallel size-scaling jobs.

**Manuscript:** Abstract; Methods rigid-strain subsection; Results $\mathcal{S}(n)$; Discussion (design implications); Table~III caption; Methods validation.

---

## Major Comment 2 — Single seed (42) placement

**Referee concern:** Quantitative periodic $\mathcal{S}(n)$ may be seed-specific; seed~137 covers only tetramers.

**Response:** We agree and have separated **qualitative** element trends from **quantitative** placement-specific magnitudes:
1. Periodic $\mathcal{S}(n)$ and the fifteen-point grid use a **fixed reference dopant-site map** (one substituent per C$_{60}$); main text no longer foregrounds RNG seed labels (Abstract, Methods, Results, Conclusions).
2. **Table~IV** is **tetramer-only** (**reference** vs.\ **alternate** placement): we **removed** any periodic $n{=}4$ column, which mixed concentrations and boundary conditions with tetramer placement controls (parallel to Major Comment~1).
3. Tetramer $\alpha$ opposite signs for N vs.\ B are reported for the **reference** placement at fixed 5\% nominal doping, with Table~IV pending to test slope sensitivity; we do **not** claim placement-averaged magnitudes for the B/N/P networks.
4. Qualitative ranking statements (P largest $|\mathcal{S}|$ at $n{=}4$ on this map; N vs.\ B $\alpha$ sign) are framed as **configuration-specific audits**, not universal dopant laws, until the alternate-placement grid converges and periodic alternate placements are added (Conclusions, future work).

**Manuscript:** Methods substitutional-doping paragraph; Results strain/synergy subsections; Discussion (i); Limitations; Table~IV; Methods validation.

**Pending DFT:** 18 seed~137 tetramer ENERGY tasks (`run_seed137_validation.sh`); periodic alternate-placement subset queued after Exp9 vertical batch.

---

## Major Comment 3 — Mechanism needs quantitative support

**Referee concern:** N/B/P coupling classes are qualitative; need bond/charge metrics and decomposition of geometric vs.\ electronic nonlinearity.

**Response:**
1. **Electronic (N vs.\ B):** Results Sec.~\ref{sec:electronic} now reports verified $\epsilon{=}0$ gaps from the Exp.~7 archive ($E_g^{\mathrm{B}}\approx 0.03$, $E_g^{\mathrm{N}}\approx -0.14$, $E_g^{\mathrm{P}}\approx 0.05$~eV) and links them to opposite $\alpha$ signs on the legacy PBE rigid tetramer grid (Table~I; ${\sim}360$~meV/\% span). Fig.~1(a,b) and Fig.~2 provide the $\pi$-DOS context.
2. **Structural (P):** Table~V expanded with $\sigma(\bar{d})$ at $+3$\% strain, showing P's frozen local environment ($\Delta\bar{d}\approx 3\times 10^{-5}$~\AA; $\sigma\approx 4\times 10^{-4}$~\AA) vs.\ B/N (${\sim}8.5\times 10^{-3}$~\AA\ mean shift; $\sigma{\sim}0.02$~\AA).
3. **Nonlinearity decomposition:** Discussion (iv)--(vi) quantify Table~V $\Delta\bar{d}$ vs.\ $|\mathcal{S}|$ contrasts, exclude tetramer--periodic $\alpha$ extrapolation (v), and state decomposition outlook (vi); Mayer bond order / Bader partitioning along the strain path remain **future work** (Limitations), so relative electronic vs.\ geometric weights are not quantified in this revision.

**Manuscript:** Results electronic subsection; Discussion (i)--(vi), validation protocol; Table~V; Fig.~2.

**Pending:** Mayer/Bader strain-path analysis (no new DFT in this revision).

---

## Major Comment 4 — Argumentation rigor

**Referee concern:** $\mathcal{S}$ vs $\alpha$ comparison mismatched; stability reordering overstated; size trends confounded by cutoff.

**Response:**
- (4.1) We **removed** the side-by-side numeric contrast between tetramer $(\alpha_\delta-\alpha_0)\epsilon$ estimates (${\sim}5$\% doping) and periodic $n{=}4$ $\mathcal{S}$ (${\sim}1.7$\% per atom) from Discussion---the referee correctly notes that concentration and boundary-condition mismatch invalidates this as a nonlinearity test. Non-additivity is argued only via Eq.~\eqref{eq:synergy_order} on matched four-corner grids.
- (4.2) Stability language tightened to **relative margins** among comparable $|E_{\mathrm{sub}}|$; B vs.\ P ranks at $\epsilon{=}0$ are **unchanged** by meV/atom $\mathcal{S}$.
- (4.3) Core claims focus on $n\leq 4$ at matched 400~Ry; $n\geq 6$ uses 350~Ry and N sign change is **excluded** from conclusions until Table~II cutoff400 control completes.

**Manuscript:** Discussion (v)--(vii), Design implications; validation protocol (Tables~II--IV); Results synergy; Conclusions.

---

## Major Comment 5 — $E_{\mathrm{sub}}$ definition

**Referee concern:** Large eV/dopant values confuse readers.

**Response:** First numeric $E_{\mathrm{sub}}$ appearance and Methods observables define it as a **fixed-strain total-energy difference without chemical potentials**, not a formation enthalpy; used only for relative comparison within the protocol.

**Manuscript:** Methods (energy observables); Results strain response; Limitations.

---

## Minor Comments (summary)

| Item | Action |
|------|--------|
| Internal paths in main text | Removed; Data Availability only (`sci-simukit` URL) |
| $\mathcal{S}$ / $\pi$ symbols | **R251**: no bare PDOS; order parameter $\mathcal{S}$; $\pi$-DOS in SI inventory; `\hyphenation` |
| References sentence case | **R252**: APS sentence case on all 22 cited keys; [15] = unique SM entry |
| $E_\mathrm{sub}$ definition | **R252**: single Methods definition; Validation cross-ref (not formation enthalpy; no $\mu$) |
| Fig.~1(c)--(d) legibility | **R250**: N $\alpha$ in-bar label; $n{=}4$ box lower-left; max $|\mathcal{S}|$ at $n{=}1$ P |
| Discussion / Conclusions length | Context compressed; Conclusions condensed (no numeric repeat) |
| Supplemental citations | Overview + Tables I--V cited; table order I--V |
| Mayer/Bader mechanism | Limitations: not computed; Table~V geometry only |
| Marcus vs $\mathcal{S}$ | Abstract states scope once; Methods/Results/Discussion no longer repeat ``orthogonal to the $\mathcal{S}$ audit (R254); $\lambda$ SI-only; B negative $\lambda^{-}$ in Limitations only (**R261**) |

---

## Pending at resubmission (computational)

| Task | Table | Status |
|------|-------|--------|
| Ionic relaxation geometry opt. | III | **running** 2/4 (`relax_P_eps0_geo` **CRIT**; OT${\sim}85$, grad${\sim}1.6\times10^{-6}$~Ha/bohr) |
| Alternate-placement ENERGY grid | IV | 18 inp (alternate archive); **pending** |
| 400~Ry $n{=}6$ N SP (Exp10 40/41) | II | **pending** |
| Marcus vertical SP (8) | Fig.~3 | **8/8** converged; eight $\lambda^{\pm}$ in Fig.~3; B $\lambda^{-}{=}{-}0.173$~eV flagged non-physical (Limitations) |
| Setup/process/result audit | `reliability_audit.json` | `bash experiments/verify_reliability.sh` (**294** pass / 2 warn; coords+inp+workflow) |

---

*Document version: PRB Major 1 response (Loop R288) (2026-06-21). Align with `cover_letter_prb.txt`.*
---

## Detailed Chinese peer-review checklist (Major Revision, 2026-06-20)

| Review theme | Action in this revision |
|--------------|-------------------------|
| **§I Abstract** | Rigid-strain upfront; ``not necessarily additive''; synergy $\mathcal{S}$ defined; $\alpha$ named; Table~III **2/4** partial; Marcus Fig.~3 boundary |
| **§II Introduction** | Periodic PBE+D3 $\mathcal{S}$ vs.\ legacy PBE tetramer $\alpha$ (Table~I) separated; upper-bound + Table~III **2/4** partial; Marcus Fig.~3; **Lv2026** survey gap vs.\ $(\epsilon,\delta)$ $\mathcal{S}$ |
| **§III Methods** | Table~I legacy PBE vs.\ periodic PBE+D3 explicit; Table~III BFGS force thresholds + OT outer SCF (Sec.~\ref{sec:methods_s3_relax}); Tables~II--IV in Methods; Marcus $E_{\mathrm{vert}}$ vs $E_{\mathrm{opt}}$ |
| **§III.C doping %** | Clarified: one substituent per C$_{60}$ $\Rightarrow$ ${\sim}1.67$ at.\% (not reviewer's 0.42% one-dopant/supercell) |
| **§III.E Table~III** | Sign-only; PBE rigid vs PBE+D3 relaxed mismatch explicit |
| **§IV structure** | No standalone Section IV; transport in Results |
| **§IV Fig.~4** | FCWD placeholder removed from main text |
| **§V Results** | Fifteen-point $\mathcal{S}(n)$ audit via Table~II; partial III pristine checkpoint (order-of-magnitude $\Delta E$); $P@\epsilon{=}0$ CRIT OT~294 |
| **§VI Discussion** | Factor of four; characterize; Table~III sign-only criterion |
| **§VIII Conclusions** | Three Intro questions closed; (2) cites max $|\mathcal{S}|=31.9$~meV/atom (P, $n{=}1$); III sign-qualitative checkpoint; future work lists Table~III P corners |

*Document version: PRB Major Revision + Chinese checklist (Loop R284, 2026-06-21).*

