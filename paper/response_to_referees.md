> **Loop C 索引**：**Report No. 2** (2026) — IDs **R2-M1…R2-M5**, **R2-m1…R2-m4**; Report No. 1 retained below as **C-M1…C-m5**.

# Response to Referees — PRB Major Revision (Report No. 2)

**Manuscript:** Non-Additive Strain--Doping Coupling in Quasi-Hexagonal C$_{60}$ Graphullerene  
**Journal:** Physical Review B (Regular Article)  
**Recommendation:** Major Revision (second round)

---

## Summary response

We thank the referee for recognizing the corrections to doping concentration, Marcus definitions, functional mismatch disclosure, and legacy-PBE vs.\ PBE+D3 separation. This revision addresses Report No. 2 notation, APS section hierarchy, language, and figure--text alignment in the manuscript; Table~III ionic-relaxation is **complete** (4/4; sign reversal of $\mathcal{S}$); alternate-placement (Table~IV) DFT remains pending.

---

## R2-Major Comment 1 — Notation ($\mathcal{S}$, $\pi$)

**Referee concern:** Lowercase $s$ vs.\ $\mathcal{S}$; garbled $\pi$ (e.g., ``71-DOS'').

**Response:** The source manuscript already uses $\mathcal{S}$ throughout (Eq.~\eqref{eq:synergy_order}); we added an explicit Methods convention that the synergy order parameter is \emph{calligraphic} $\mathcal{S}$, never Latin $s$. All densities of states are written $\pi$-DOS (Methods, Fig.~\ref{fig:pdos} captions). We recompiled the PDF and verified no bare ``PDOS'' or broken $\pi$ strings remain in main-text \texttt{.tex}.

**Manuscript:** Methods `sec:notation`; SI/main $\pi$-DOS inventory.

---

## R2-Major Comment 2 — Section hierarchy and internal labels

**Referee concern:** Numbered ``1.--4.'' subsections under Methods; unnumbered Results paragraph; `RUN_TYPE`, `Exp.~X`, file paths.

**Response:** (i) Moved detailed protocol blocks into a dedicated Methods subsection **Detailed calculation protocols** so ionic-relaxation, alternate-placement, and Marcus steps use standard `\subsubsection` hierarchy. (ii) Promoted the Results ionic-relaxation block to `\subsubsection{Ionic-relaxation checkpoint (partial)}`. (iii) Replaced `RUN_TYPE` literals with standard task names (single-point total-energy evaluations; fixed-cell geometry optimization). (iv) Main-text `Exp.~` labels and repository paths were removed in prior revisions; Table~II rows now separate IPR (open data) from $J$ (Fig.~\ref{fig:j}).

**Manuscript:** `methods_extended.tex`; Results `sec:relax_checkpoint`; Table~II.

---

## R2-Major Comment 3 — Mechanistic electronic-structure evidence

**Referee concern:** Qualitative mechanism only; need Mayer/Bader/bond order.

**Response:** We expanded sign-conflict physics in Discussion (iii) and Design implications (B/N $n{=}4$), retain Table~V $\Delta\bar{d}$/$\sigma(\bar{d})$ and $\pi$-DOS/gap context (Results + Fig.~\ref{fig:pdos}), and **reiterate** that Mayer bond order and Bader partitioning along the strain path are not yet computed (Limitations). No new DFT in this pass.

**Pending:** Mayer/Bader strain-path analysis (Track A backlog).

---

## R2-Major Comment 4 — Periodic configuration generality

**Referee concern:** Single periodic placement; tetramer-only alternate seed.

**Response:** Unchanged scientific stance from Report No. 1: all periodic $|\mathcal{S}|$ magnitudes are **configuration-specific** on the fixed reference map; Table~IV tests tetramer placement only. Qualitative donor/acceptor trends are separated from quantitative magnitudes (Methods, Results, Conclusions). Periodic alternate-placement subset remains future work.

**Pending:** seed~137 tetramer grid (Table~IV); optional periodic alternate placement.

---

## R2-Major Comment 5 — Incomplete ionic relaxation

**Referee concern:** incomplete Table~III; no periodic relax; upper bounds only.

**Response:** We agree. All main-text $|\mathcal{S}|$ remain **protocol upper bounds**; Table~III is **sign-qualitative** with cross-functional rigid (legacy PBE) vs.\ relaxed (PBE+D3) corners. Fixed-cell geometry optimization on all four corners is **complete** (pristine $\epsilon{=}0,+3$\% and $P$ $\epsilon{=}0,+3$\%): $\mathcal{S}_{\mathrm{rigid}}=+0.96$~meV/atom versus $\mathcal{S}_{\mathrm{relaxed}}=-2.28$~meV/atom (**sign not preserved**). The $P$ $\epsilon{=}0$ corner required one outer-SCF restart; the $P$ $\epsilon{=}3$\% corner required continuation past a 300-step BFGS cap (450-step restart). Queue details do not alter the sign-qualitative interpretation protocol. A matched-functional rigid grid remains future work before any quantitative retention ratio.

**DFT status:** Table~III **4/4** (`relax_validation/`; `relax_validation_tetramer.json`).

---

## R2-Minor / Technical (summary)

| ID | Issue | Action (R316) |
|----|-------|----------------|
| R2-m1 | Duplicate refs [9],[19],[22] | Clean `latexmk` rebuild: **27** unique `\bibitem` entries in `.bbl`; no duplicate keys in `.bib` |
| R2-m2 | $|\mathcal{S}|/E_{\mathrm{sub}}$ scale mismatch | Moved ratio from Methods to Discussion (vii) as **rough estimate only** |
| R2-m3 | Table I/II formatting | Table~II IPR/$J$ row split; Table~I structure unchanged (already ruledtabular) |
| R2-m4 | Sign-conflict physics | Expanded Discussion (N $\mathcal{S}$ sign change) + Design implications (B/N) |
| R2-t1 | Typography / hyphenation | Added `\hyphenation{stress-related, placement-sensitive, sign-change}` |
| R2-t2 | ``gate interpretation'' | → ``govern interpretation'' (Methods validation) |
| R2-t3 | Abstract awkward bound/predict | Unified **serve as upper bounds---not predictions---** (Abstract, Methods, Intro L65, Conclusions; R316--R325) |
| R2-t4 | Fig.~4 $J$ without IPR | Fig.~\ref{fig:j} caption + Methods: IPR in open data; $J$ in figure |
| R2-t5 | Discussion `\textbf{(i)}` / `\textbf{Table~}` blocks | → `\paragraph{}` + enumerated Conclusions (1)--(3) |

---

# Response to Referees — PRB Major Revision (Report No. 1, archive)

**Manuscript:** Non-Additive Strain--Doping Coupling in Quasi-Hexagonal C$_{60}$ Graphullerene  
**Journal:** Physical Review B (Regular Article)

---

## Major Comment 1 — Rigid strain lacks relaxation validation

**Referee concern:** All $\alpha$ and $\mathcal{S}$ use fixed fractional coordinates; no relax benchmark; reported $|\mathcal{S}|$ may be an upper bound.

**Response:** We agree that fixed fractional coordinates can overestimate strain coupling and that equilibrium relevance must be demonstrated. We have (i) relabeled all main-text $|\mathcal{S}|$ magnitudes as **protocol upper bounds** at fixed coordinates (Abstract, Methods, Results, Discussion design language); (ii) **removed** the prior rhetorical contrast between the archived rigid tetramer Table~III entry ($\mathcal{S}=+0.96$~meV/atom) and periodic $n{=}4$ $P$ ($-23.7$~meV/atom), which the referee correctly notes is **not** a valid control because concentration and boundary conditions differ; and (iii) completed **Table~III** as a **sign-qualitative** tetramer benchmark: rigid references use legacy PBE (no D3) whereas relaxed corners use PBE+D3, so a quantitative $|\mathcal{S}_{\mathrm{relaxed}}|/|\mathcal{S}_{\mathrm{rigid}}|$ ratio is **not** claimed; with all four fixed-cell corners converged, $\mathcal{S}_{\mathrm{relaxed}}=-2.28$~meV/atom **reverses** the rigid $+0.96$~meV/atom sign, supporting the upper-bound reading of rigid-strain $|\mathcal{S}|$. Marcus vertical SP (8/8) is complete.

**Manuscript:** Abstract; Methods rigid-strain subsection; Results $\mathcal{S}(n)$; Discussion (design implications); Table~III caption; Methods validation.

---

## Major Comment 2 — Single seed (42) placement

**Referee concern:** Quantitative periodic $\mathcal{S}(n)$ may be seed-specific; seed~137 covers only tetramers.

**Response:** We agree and have separated **qualitative** element trends from **quantitative** placement-specific magnitudes:
1. Periodic $\mathcal{S}(n)$ and the fifteen-point grid use a **fixed reference dopant-site map** (one substituent per C$_{60}$); main text no longer foregrounds RNG seed labels (Abstract, Methods, Results, Conclusions).
2. **Table~IV** is **tetramer-only** (**reference** vs.\ **alternate** placement): we **removed** any periodic $n{=}4$ column, which mixed concentrations and boundary conditions with tetramer placement controls (parallel to Major Comment~1). Reference-placement $\mathcal{S}_{+3\%}^{\mathrm{tet}}$ on the legacy rigid grid is now reported in Results ($+3.8$, $+5.7$, $+1.0$~meV/atom for B, N, and P) as a placement-audit baseline only. The pending alternate grid uses PBE+D3 rigid single-points on an independent seed-137 map (Methods Sec.~\ref{sec:methods_s4_seed}), not the legacy-PBE archive of Table~\ref{tab:I}.
3. Tetramer $\alpha$ opposite signs for N vs.\ B are reported for the **reference** placement at fixed 5\% nominal doping, with Table~IV pending to test slope sensitivity; we do **not** claim placement-averaged magnitudes for the B/N/P networks.
4. Qualitative ranking statements (P largest $|\mathcal{S}|$ at $n{=}4$ on this map; N vs.\ B $\alpha$ sign) are framed as **configuration-specific audits**, not universal dopant laws, until the alternate-placement grid converges and periodic alternate placements are added (Conclusions, future work).

**Manuscript:** Methods substitutional-doping paragraph; Results strain/synergy subsections; Discussion (i); Limitations; Table~IV; Methods validation.

**Pending DFT:** 18 seed~137 tetramer ENERGY tasks **in progress** (0/18 converged; first task running); periodic alternate-placement subset deferred until the tetramer grid completes.

---

## Major Comment 3 — Mechanism needs quantitative support

**Referee concern:** N/B/P coupling classes are qualitative; need bond/charge metrics and decomposition of geometric vs.\ electronic nonlinearity.

**Response:**
1. **Electronic (N vs.\ B):** Results Sec.~\ref{sec:electronic} now reports verified $\epsilon{=}0$ gaps from the archived tetramer electronic-structure set ($E_g^{\mathrm{B}}\approx 0.03$, $E_g^{\mathrm{N}}\approx -0.14$, $E_g^{\mathrm{P}}\approx 0.05$~eV) and links them to opposite $\alpha$ signs on the legacy PBE rigid tetramer grid (Table~I; ${\sim}360$~meV/\% span). Fig.~\ref{fig:main}(a,b) and Fig.~\ref{fig:pdos} provide the $\pi$-DOS context.
2. **Structural (P):** Table~V expanded with $\sigma(\bar{d})$ at $+3$\% strain, showing P's frozen local environment ($\Delta\bar{d}\approx 3\times 10^{-5}$~\AA; $\sigma\approx 4\times 10^{-4}$~\AA) vs.\ B/N (${\sim}8.5\times 10^{-3}$~\AA\ mean shift; $\sigma{\sim}0.02$~\AA).
3. **Nonlinearity decomposition:** Discussion (iv)--(vi) quantify Table~V $\Delta\bar{d}$ vs.\ $|\mathcal{S}|$ contrasts, exclude tetramer--periodic $\alpha$ extrapolation (v), and state decomposition outlook (vi); Design implications cross-reference the completed Table~III ionic-relaxation benchmark (sign reversal; Major Comment~1); Mayer bond order / Bader partitioning along the strain path remain **future work** (Limitations), so relative electronic vs.\ geometric weights are not quantified in this revision.

**Manuscript:** Results electronic subsection; Discussion (i)--(vi), validation protocol; Table~V; Fig.~\ref{fig:pdos}.

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
| Fig.~1(c)--(d) legibility | **R250/R309**: N $\alpha$ in-bar label; $n{=}4$ box lower-left; peak $|\mathcal{S}|$ at $n{=}1$ P; caption (a) $E_g$ / (d) inset 读图键 |
| Fig.~3 Marcus EA arrow | **R303/R308**: cross-dopant column legend; adiabatic IP arrow + EA text (B/P); $\lambda^{\pm}$ boxes; neutral-$Q$ band for vertical SP |
| Discussion / Conclusions length | Context compressed; Conclusions condensed (no numeric repeat) |
| Supplemental citations | Overview + Tables I--V cited; table order I--V |
| Mayer/Bader mechanism | Limitations: not computed; Table~V geometry only |
| Marcus vs $\mathcal{S}$ | Abstract states scope once; Methods/Results/Discussion no longer repeat ``orthogonal to the $\mathcal{S}$ audit (R254); $\lambda$ SI-only; B negative $\lambda^{-}$ in Limitations only (**R261**) |

---

## Pending at resubmission (computational)

| Task | Table | Status |
|------|-------|--------|
| Ionic relaxation geometry opt. | III | **complete** 4/4; $\mathcal{S}_{\mathrm{relaxed}}=-2.28$ vs rigid $+0.96$ meV/atom (sign not preserved) |
| Alternate-placement ENERGY grid | IV | 18 inp (alternate archive); **pending** |
| 400~Ry $n{=}6$ N SP (Exp10 40/41) | II | **pending** |
| Marcus vertical SP (8) | Fig.~3 | **8/8** converged; eight $\lambda^{\pm}$ in Fig.~3; B $\lambda^{-}{=}{-}0.173$~eV flagged non-physical (Limitations) |
| Setup/process/result audit | `reliability_audit.json` | `bash experiments/verify_reliability.sh` (**294** pass / 2 warn; coords+inp+workflow) |

---

## Detailed Chinese peer-review checklist (Major Revision, 2026-06-20)

| Review theme | Action in this revision |
|--------------|-------------------------|
| **§I Abstract** | Covalent-network framing（R328）；Table~III **4/4** sign reversal；Table~IV pending；``at fixed coordinates'' on max $|\mathcal{S}|$; Marcus Fig.~3 boundary |
| **§II Introduction** | Periodic PBE+D3 $\mathcal{S}$ vs.\ legacy PBE tetramer $\alpha$ (Table~I) separated; Table~III **4/4** complete (sign reversal); Table~IV pending |
| **§III Methods** | Table~I legacy PBE vs periodic PBE+D3; Tables~III--IV upper-bound gate in `sec:notation`（R318）；Table~III four-corner + BFGS thresholds; **Table~IV** reference legacy-PBE vs alternate PBE+D3 seed~137 (`sec:methods_s4_seed`); Fig.~3 Marcus slanted IP + neutral-$Q$ band schematic (R308--R315) |
| **§III.C Doping concentration** | Clarified: one substituent per C$_{60}$ $\Rightarrow$ $n$ in $60n$ atoms (${\sim}1.67$ at.\%); explicitly \emph{not} $1/240{=}0.42$ at.\% single-dopant/supercell counting |
| **§III.E Table~III** | Sign-only; PBE rigid vs PBE+D3 relaxed; four corners = pristine + $P$ at $\epsilon{=}0,+3$\% |
| **§IV Structure** | No standalone Section IV; transport in Results |
| **§IV Fig.~4** | FCWD placeholder removed from main text |
| **§V Results** | Fifteen-point $\mathcal{S}(n)$ (Table~II); opener Tables~III--IV gate（R319）；$n{=}4$ reference vs seed-137 alternate 措辞；Table~III partial sign-only cross-functional 句；Fig.~3 cross-dopant Marcus schematic; Fig.~1 (a) $E_g$ / (d) peak $|\mathcal{S}|$ callouts (R309) |
| **§VI Discussion** | Factor of four; Table~III/IV gate 与 Results R319 交叉引用；**Katiyar2025** + **LopezAlcalay2025** 分调 vs 四隅 $\mathcal{S}$；Validation 段 `\paragraph{Table III/IV/II}` 层级（R316）；Mechanistic synthesis `\paragraph{}` 替代 `\textbf{(i)}`（R316）；Design implications Tables~III--IV（R320） |
| **§VIII Conclusions** | `enumerate` 三条对应 Intro；upper-bound **serve as upper bounds---not predictions---**（R316）；Table~III four-corner sign-only; Table~IV reference $\mathcal{S}_{+3\%}^{\mathrm{tet}}$ archived; future work decouples Table~IV placement vs.\ XC (R314) |

*Document version: PRB Major Revision + Chinese checklist (Loop R316, 2026-06-19). Align with `cover_letter_prb.txt`.*

