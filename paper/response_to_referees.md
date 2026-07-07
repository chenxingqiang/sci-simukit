> **Loop C 索引**：**Report No. 2** (2026) — IDs **R2-M1…R2-M5**, **R2-m1…R2-m4**; Report No. 1 retained below as **C-M1…C-m5**.

# Response to Referees — PRB Major Revision (Report No. 2)

**Manuscript:** Non-Additive Strain--Doping Coupling in Quasi-Hexagonal C$_{60}$ Graphullerene  
**Journal:** Physical Review B (Regular Article)  
**Recommendation:** Major Revision (second round)

---

## Summary response

We thank the referee for recognizing the corrections to doping concentration, Marcus definitions, functional mismatch disclosure, and legacy-PBE vs.\ PBE+D3 separation. This revision addresses Report No.~2 notation, APS section hierarchy, language, and figure--text alignment; **Table~III** tetramer ionic-relaxation is **complete** (4/4; sign reversal of $\mathcal{S}$); **Table~IV** alternate-placement DFT is **complete** (24/24). We further upgraded the narrative from a single-qHP case study to a **covalent molecular-network** coupling framework (internal vs.\ external stress field, mismatch--$|\mathcal{S}|$ scaling, additive-model applicability boundaries, and qualitative experimental signatures in new Methods/Discussion subsections). Main-text transport/$J$ content is consolidated in the **Supplemental Material**; Fig.~3 in the main text reports the Marcus protocol schematic and tabulated $\lambda^{\pm}$ only.

**New DFT in this pass:** periodic $n{=}1$ $P$ four-corner fixed-cell geometry optimization (**4/4** complete); Hirshfeld population along the strain path for **B**, **N**, and **P** at $n{=}1$ (**18/18** complete); reference-placement PBE+D3 tetramer $\alpha$ grid (**partial** 6/24; $\epsilon{=}0$ and $+2.5$\% B/N converged; $+2.5$\% P in progress with outer-SCF cycling).

**Manuscript alignment (this pass):** Fig.~1(c) now uses **PBE+D3 alternate-placement** $\alpha$ (Table~IV) instead of legacy PBE Table~I; explicit **decoupling** definition (not $\alpha$--$|\mathcal{S}|$ anticorrelation); $\mathcal{S}_{\mathrm{vdW}}\approx +0.33$~meV/atom from D3 corner extraction; Eshelby/defect-elastic framing; Table~V tetramer-proxy disclaimer; $n\leq 4$ non-monotonic $|\mathcal{S}|$ note; raw $\Delta E_{\mathrm{sub}}$ terminology.

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

**Response:** We expanded sign-conflict physics in Discussion (iii) and Design implications (B/N $n{=}4$), retain Table~V $\Delta\bar{d}$/$\sigma(\bar{d})$ with explicit **tetramer-proxy** scope (not periodic $n{=}1$ bond statistics), and added **$\mathcal{S}_{\mathrm{vdW}}\approx +0.33$~meV/atom** on the matched-functional $P$ tetramer grid (negligible vs.\ total $|\mathcal{S}|$). Hirshfeld charge strain-path audits for $n{=}1$ **B**, **N**, and **P** are **complete** (18/18): P shows the largest fractional shift under tension ($+0.063\to+0.056\,e$ at $+3$\%); B and N shift more modestly ($+0.12\to+0.11\,e$ and $+0.069\to+0.057\,e$). Sign-origin paragraphs distinguish geometric (P) vs.\ electronic (B/N) channels. Mayer/Bader remain **future work**.

**Pending:** Mayer/Bader analysis (Track A backlog).

**Manuscript:** Discussion mechanistic synthesis; `sec:methods_population`; Limitations.

---

## R2-Major Comment 4 — Periodic configuration generality

**Referee concern:** Single periodic placement; tetramer-only alternate seed.

**Response:** Unchanged scientific stance from Report No.~1: all periodic $|\mathcal{S}|$ magnitudes are **configuration-specific** on the fixed reference map; Table~IV tests tetramer placement only. Qualitative donor/acceptor trends are separated from quantitative magnitudes (Methods, Results, Conclusions). Periodic alternate-placement subset is **complete** (16/16; Table~II); tetramer alternate grid **complete** (24/24).

**Pending:** optional additional periodic placement seeds beyond the audited maps.

---

## R2-Major Comment 5 — Incomplete ionic relaxation

**Referee concern:** incomplete Table~III; no periodic relax; upper bounds only.

**Response:** We agree. Main-text rigid $|\mathcal{S}|$ are **protocol upper bounds** at fixed coordinates. **Table~III** tetramer fixed-cell geometry optimization is **complete** (4/4): $\mathcal{S}_{\mathrm{rigid}}=+0.96$~meV/atom versus $\mathcal{S}_{\mathrm{relaxed}}=-2.28$~meV/atom (**sign not preserved**). Matched-functional PBE+D3 rigid single-points on the same four corners give $\mathcal{S}_{\mathrm{rigid}}^{\mathrm{PBE+D3}}=+1.19$~meV/atom ($|\mathcal{S}_{\mathrm{relaxed}}|/|\mathcal{S}_{\mathrm{rigid}}^{\mathrm{PBE+D3}}|\approx 1.9$; sign still not preserved). **Periodic** $n{=}1$ $P$ four-corner fixed-cell geometry optimization is **complete** (4/4): $\mathcal{S}_{\mathrm{rigid}}=-31.9$~meV/atom versus $\mathcal{S}_{\mathrm{relaxed}}\approx +0.1$~$\mu$eV/atom ($|\mathcal{S}_{\mathrm{relaxed}}|/|\mathcal{S}_{\mathrm{rigid}}|\lesssim 10^{-5}$), so rigid periodic $|\mathcal{S}|$ is a conservative upper bound on equilibrium $\mathcal{S}$ in this cell (Sec.~\ref{sec:relax_checkpoint}).

**DFT status:** Table~III tetramer **4/4**; periodic $n{=}1$ P **4/4**; reference-placement PBE+D3 tetramer grid **partial** 6/24 ($\epsilon{=}0$ pristine/B/N/P; $+2.5$\% B/N; $+2.5$\% P outer-SCF oscillation in progress).

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
| R2-t4 | Fig.~4 $J$ without IPR | $J$/transport moved to **Supplemental Material**; main Fig.~3 Marcus protocol + $\lambda$ table only |
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
2. **Table~IV** is **tetramer-only** (**reference** vs.\ **alternate** placement): we **removed** any periodic $n{=}4$ column, which mixed concentrations and boundary conditions with tetramer placement controls (parallel to Major Comment~1). Reference-placement $\mathcal{S}_{+3\%}^{\mathrm{tet}}$ on the legacy rigid grid is now reported in Results ($+3.8$, $+5.7$, $+1.0$~meV/atom for B, N, and P) as a placement-audit baseline only. The alternate grid uses PBE+D3 rigid single-points on an independent seed-137 map (Methods Sec.~\ref{sec:methods_s4_seed}), not the legacy-PBE archive of Table~\ref{tab:I}.
3. Tetramer $\alpha$ opposite signs for N vs.\ B are reported for the **reference** placement at fixed 5\% nominal doping, with Table~IV complete (24/24) to test slope sensitivity; we do **not** claim placement-averaged magnitudes for the B/N/P networks.
4. Qualitative ranking statements (P largest $|\mathcal{S}|$ at $n{=}4$ on this map; N vs.\ B $\alpha$ sign) are framed as **configuration-specific audits**, not universal dopant laws, with periodic alternate placements complete (16/16; Table~II) and the tetramer alternate grid complete (24/24) (Conclusions, future work).

**Manuscript:** Methods substitutional-doping paragraph; Results strain/synergy subsections; Discussion (i); Limitations; Table~IV; Methods validation.

**DFT status (R385):** seed-137 tetramer alternate grid **complete** (18/18 dopant strain points + 6/6 modern PBE+D3 pristine references); Table~IV alternate $\alpha$ and $\mathcal{S}_{+3\%}^{\mathrm{tet}}$ populated in the manuscript.

---

## Major Comment 3 — Mechanism needs quantitative support

**Referee concern:** N/B/P coupling classes are qualitative; need bond/charge metrics and decomposition of geometric vs.\ electronic nonlinearity.

**Response:**
1. **Electronic (N vs.\ B):** Results Sec.~\ref{sec:electronic} now reports verified $\epsilon{=}0$ gaps from the archived tetramer electronic-structure set ($E_g^{\mathrm{B}}\approx 0.03$, $E_g^{\mathrm{N}}\approx -0.14$, $E_g^{\mathrm{P}}\approx 0.05$~eV) and links them to opposite $\alpha$ signs on the legacy PBE rigid tetramer grid (Table~I; ${\sim}360$~meV/\% span). Fig.~\ref{fig:main}(a,b) and Fig.~\ref{fig:pdos} provide the $\pi$-DOS context.
2. **Structural (P):** Table~V expanded with $\sigma(\bar{d})$ at $+3$\% strain, showing P's frozen local environment ($\Delta\bar{d}\approx 3\times 10^{-5}$~\AA; $\sigma\approx 4\times 10^{-4}$~\AA) vs.\ B/N (${\sim}8.5\times 10^{-3}$~\AA\ mean shift; $\sigma{\sim}0.02$~\AA).
3. **Nonlinearity decomposition:** Discussion (iv)--(vi) quantify Table~V $\Delta\bar{d}$ vs.\ $|\mathcal{S}|$ contrasts, exclude tetramer--periodic $\alpha$ extrapolation (v), and state decomposition outlook (vi); Design implications cross-reference the completed Table~III ionic-relaxation benchmark (sign reversal; Major Comment~1); Mayer bond order / Bader partitioning along the strain path remain **future work** (Limitations), so relative electronic vs.\ geometric weights are not quantified in this revision.

**Manuscript:** Results electronic subsection; Discussion (i)--(vi), validation protocol; Table~V; Fig.~\ref{fig:pdos}.

**Pending:** Mayer/Bader strain-path analysis (no new DFT beyond Hirshfeld grids).

**Manuscript:** Results electronic subsection; Discussion (i)--(vi), `sec:stress_coupling`, `sec:generality`; Table~V; Fig.~\ref{fig:pdos}; `sec:methods_population`.

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
| Fig.~1(c)--(d) legibility | **R250/R309**: N $\alpha$ in-bar label; $n{=}4$ box lower-left; peak $|\mathcal{S}|$ at $n{=}1$ P; caption (a) $E_g$ / (d) panel annotation 读图键 |
| Fig.~3 Marcus | **R390**: single protocol schematic (panel a) + tabulated IP/EA/$\lambda^{\pm}$ (panel b); B $\lambda^{-}$ excluded in table |
| Discussion / Conclusions length | Context compressed; Conclusions condensed (no numeric repeat) |
| Supplemental citations | Overview + Tables I--V cited; table order I--V |
| Mayer/Bader mechanism | Limitations: not computed; Table~V geometry only |
| Marcus vs $\mathcal{S}$ | Abstract states scope once; Methods/Results/Discussion no longer repeat ``orthogonal to the $\mathcal{S}$ audit (R254); $\lambda$ SI-only; B negative $\lambda^{-}$ in Limitations only (**R261**) |

---

## Pending at resubmission (computational)

| Task | Table | Status |
|------|-------|--------|
| Alternate placement (seed~137) | IV | **complete** 24/24; N $\alpha$ sign reversal; $|\alpha_P|\sim 10^3$~meV/\% |
| Ionic relaxation geometry opt. | III | **complete** 4/4; $\mathcal{S}_{\mathrm{relaxed}}=-2.28$ vs rigid $+0.96$ meV/atom (sign not preserved) |
| Alternate-placement ENERGY grid | IV | **complete** 24/24 (PBE+D3 rigid) |
| 400~Ry $n{=}6$ N SP (Exp10 41/41) | II | **complete** |
| Marcus vertical SP (8) | Fig.~3 | **8/8** converged; $\lambda^{\pm}$ tabulated in Fig.~3(b); B $\lambda^{-}{=}{-}0.173$~eV flagged non-physical (Limitations) |
| Matched-functional rigid PBE+D3 (Table III) | III | **complete** 4/4; ratio $\approx 1.9$ (sign not preserved) |
| Population Hirshfeld ($n{=}1$ B/N/P) | V / II | **complete** 18/18 |
| Periodic ionic relax ($n{=}1$ P) | II / III | **complete** 4/4; $\mathcal{S}_{\mathrm{rel}}\ll \mathcal{S}_{\mathrm{rig}}$ |
| Physics-upgrade narrative | Intro/Disc. | **complete** (`sec:stress_coupling`, `sec:generality`, `sec:exp_signatures`) |
| Reference placement PBE+D3 ($\alpha$ modernization) | I / II | **partial** 6/24 ($\epsilon{=}0$, $+2.5$\% B/N); $+2.5$\% P outer-SCF cycling; Table~\ref{tab:I} legacy-PBE retained until complete |
| Transport / $J$ main text | SI | **complete** (Marcus/$J$ in Supplemental Material; main Fig.~3 protocol only) |
| Setup/process/result audit | reliability audit | **294** pass / 2 warn |

---

## Detailed Chinese peer-review checklist (Major Revision, 2026-06-20)

| Review theme | Action in this revision |
|--------------|-------------------------|
| **§I Abstract** | Covalent-network framing（R328）；Table~III **4/4** sign reversal；Table~IV **24/24** alternate；``at fixed coordinates'' on max $|\mathcal{S}|$; Marcus Fig.~3 boundary |
| **§II Introduction** | Periodic PBE+D3 $\mathcal{S}$ vs.\ legacy PBE tetramer $\alpha$ (Table~I) separated; Table~III **4/4** complete (sign reversal); Table~IV alternate **24/24** |
| **§III Methods** | Table~I legacy PBE vs periodic PBE+D3; Tables~III--IV upper-bound gate in `sec:notation`（R318）；Table~III four-corner + BFGS thresholds; **Table~IV** reference legacy-PBE vs alternate PBE+D3 seed~137 (`sec:methods_s4_seed`); Fig.~3 Marcus schematic + $\lambda$ table (R390); Table~IIarchive for superseded grids |
| **§III.C Doping concentration** | Clarified: one substituent per C$_{60}$ $\Rightarrow$ $n$ in $60n$ atoms (${\sim}1.67$ at.\%); explicitly \emph{not} $1/240{=}0.42$ at.\% single-dopant/supercell counting |
| **§III.E Table~III** | Sign-only; PBE rigid vs PBE+D3 relaxed; four corners = pristine + $P$ at $\epsilon{=}0,+3$\% |
| **§IV Structure** | No standalone Section IV; transport in Results |
| **§IV Fig.~4** | FCWD placeholder removed from main text |
| **§V Results** | Fifteen-point $\mathcal{S}(n)$ (Table~II); opener Tables~III--IV gate（R319）；$n{=}4$ reference vs seed-137 alternate 措辞；Table~III partial sign-only cross-functional 句；Fig.~3 Marcus protocol + $\lambda$ table; Fig.~1 (a) $E_g$ / (d) peak $|\mathcal{S}|$ callouts (R309) |
| **§VI Discussion** | Factor of four; Table~III/IV gate 与 Results R319 交叉引用；**Katiyar2025** + **LopezAlcalay2025** 分调 vs 四隅 $\mathcal{S}$；Validation 段 `\paragraph{Table III/IV/II}` 层级（R316）；Mechanistic synthesis `\paragraph{}` 替代 `\textbf{(i)}`（R316）；Design implications Tables~III--IV（R320） |
| **§VIII Conclusions** | `enumerate` 三条对应 Intro；upper-bound **serve as upper bounds---not predictions---**（R316）；Table~III four-corner sign-only; Table~IV reference $\mathcal{S}_{+3\%}^{\mathrm{tet}}$ archived; future work decouples Table~IV placement vs.\ XC (R314) |

*Document version: PRB Major Revision + Chinese checklist (Loop R316, 2026-06-19). Align with `cover_letter_prb.txt`.*

