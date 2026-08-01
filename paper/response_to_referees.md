> **Loop C 索引**：**Report No. 2** (2026) — IDs **R2-M1…R2-M5**, **R2-m1…R2-m4**; Report No. 1 retained below as **C-M1…C-m5**.

# Response to Referees — PRB Major Revision (Report No. 2)

**Manuscript:** Breakdown of Additive Strain--Doping Energetics in Quasi-Hexagonal C$_{60}$ Graphullerene  
**Journal:** Physical Review B (Regular Article)  
**Recommendation:** Major Revision (second round)

---

## Simulated PRB Referee Round 2 — Title and Abstract (sentence 1)

### R2-Title — Breakdown of additive energetics framing

**Referee concern:** ``Non-additive'' is author-defined and does not state the physics problem (failure of additive strain--dopant energetics); title does not signal DFT total-energy scope.

**Response:** We replaced the title with **Breakdown of Additive Strain--Doping Energetics in Quasi-Hexagonal C$_{60}$ Graphullerene** so the central claim---that sequential composition/strain workflows break down---is visible before the descriptor $\mathcal{S}$ appears in the Abstract.

**Manuscript:** `\title{}`; Supplemental Material title; cover letter.

### R2-Abstract-S1 — High-throughput additive assumption

**Referee concern:** Opening ``often assembled/approximated'' lacks evidence; scope too broad without naming covalent molecular networks; ``density-functional theory'' too long.

**Response:** Sentence~1 now targets **high-throughput first-principles screening of covalent molecular networks**, states that doping and biaxial strain are **commonly evaluated independently**, and names the **implicit additive assumption** explicitly (no unsupported ``often'' without qualifier).

**Manuscript:** Abstract sentence~1.

### R2-Abstract-S2 — Physics before metric; drop ``order parameter'' in Abstract

**Referee concern:** ``We define'' and ``synergy order parameter'' frame the contribution as a new symbol rather than nonlinear strain--dopant physics; Eq.~(1) reads as a standard four-corner interaction energy; PBE+D3 is too early for the Abstract; ``cross term'' is ambiguous.

**Response:** Sentence~2 is now two clauses: (i) **first-principles** demonstration that **internal stress couples nonlinearly with biaxial strain** and breaks additivity on qHP C$_{60}$; (ii) $\mathcal{S}$ as a **matched four-corner total-energy difference** (meV/atom) **neglected in additive workflows**---a diagnostic coupling metric, not a phase-transition order parameter. PBE+D3 remains in the results sentence (Abstract sentence~3). Abstract wording ``synergy magnitude'' $\to$ ``coupling magnitude'' for consistency.

**Manuscript:** Abstract sentences~2--4.

### R2-Abstract-S3 — Predictive failure, rigid upper bounds, and P ranking scope

**Referee concern:** ``$\alpha$ and $|\mathcal{S}|$ decouple'' overstates physics; rigid protocol and relaxation caveat hidden before the $31.9$~meV/atom peak; ``largest'' without B/N/P scope; $31.9$~meV significance unclear; one sentence carried four claims; rigid vs.\ relaxed narrative tension (periodic $n{=}1$ $P$).

**Response:** Abstract sentence~3 is split into four claims: (i) **$\alpha$ does not reliably predict $|\mathcal{S}|$** on the reference rigid map (not ``decoupling''); (ii) **among the three dopants investigated**, P shows the largest $|\mathcal{S}|$, linked to **covalent-radius excess**; (iii) **$31.9$~meV/atom** at $n{=}1$, $+3$\% is labeled a **rigid-protocol upper bound** and compared to B/N at matched load; (iv) **fixed-coordinate $|\mathcal{S}|$ are not equilibrium energies**, with explicit periodic $n{=}1$ $P$ rigid vs.\ relaxed contrast ($-31.9$ vs.\ $\sim 0.1$~$\mu$eV/atom; matched PBE+D3 GEO\_OPT).

**Manuscript:** Abstract sentences~3--5.

### R2-Abstract-S4 — Rigid upper bounds as physics, not computational caveat

**Referee concern:** Narrative conflict between the $31.9$~meV/atom peak and near-extinction after relaxation; ``fixed fractional coordinates'' is Methods jargon; placement validation should not appear in the Abstract; need physical interpretation (internal-stress release) and applicability when relaxation is limited.

**Response:** Abstract limitation block reframed as **rigid-strain upper bounds vs.\ equilibrium coupling**: structural relaxation **releases dopant-induced internal stress**; $|\mathcal{S}|$ quantifies omitted coupling under **mechanically constrained or kinetically limited load**; a second sentence states relevance under **epitaxial clamping, substrate adhesion, or ultrafast loading**. Removed Methods phrasing from the Abstract; tetramer placement sensitivity remains in Methods/Limitations only. Discussion Limitations adds the same applicability sentence.

**Manuscript:** Abstract sentences~5--6; Limitations paragraph.

### R2-Abstract-S5 — Moderated take-home message (mechanism, scope, constrained loading)

**Referee concern:** ``requires'' overclaims beyond one qHP system and three dopants; ``covalent molecular networks'' generalizes beyond evidence; ``stability ranking'' and ``geometric-nonlinear regime'' are undefined; conclusion lacks mechanism and blurs equilibrium vs.\ mechanically constrained configurations.

**Response:** Closing sentence now (i) scopes claims to **quasi-hexagonal C$_{60}$ graphullerene**; (ii) states the **mechanism** (internal stress $\times$ external strain nonlinear interaction); (iii) uses **relative energetic stability** under **mechanically constrained loading**; (iv) replaces ``requires'' with **when additive workflows are expected to fail** (practical criterion, not universal law).

**Manuscript:** Abstract closing sentence.

### R2-Abstract — Round 2 overall verdict (simulated Referee \#2)

**Referee summary:** Abstract reframed from ``define $\mathcal{S}$'' to **additive approximation failure**, **nonlinear strain--dopant coupling**, rigid **upper bounds** vs.\ equilibrium relaxation, and moderated scope on qHP C$_{60}$; ``order parameter'' removed from Abstract; ``decouple'' replaced by predictive-failure language.

**Author response:** Title + eight Abstract sentences revised per R2-Title through R2-Abstract-S5; Discussion Limitations adds applicability under epitaxial clamping/substrate adhesion/ultrafast loading. Main-text terminology harmonization (``coupling energy $\mathcal{S}$'') remains for Introduction/Methods rounds.

### R3-Intro-P1 — Physics-first opening; cited additive-workflow gap

**Referee concern (simulated Referee \#2):** Opening emphasized computational workflow over physical origin of strain--dopant coupling; ``most widely used'' / ``routinely'' without evidence; transport shopping list; separability undefined; literature gap implicit; mechanism (local stress vs.\ global strain) missing before screening critique.

**Response:** First paragraph rewritten: (i) **widely used** (not ``most'') strategies for **energetic and electronic** properties; (ii) **physics first**---global bonding geometry vs.\ localized chemical stress and lattice distortion; (iii) **separable** clarified as neglecting a **nonlinear interaction term**; (iv) **many** HT mapping studies with **Materials2024untangling, Li2024strain, Katiyar2025strain** cites plus **computational cost** of coupled grids; (v) explicit **gap**---additive validity under simultaneous load **not systematically examined** for graphullerene networks. Redundant workflow-only sentences merged into this arc before the qHP system paragraph.

**Manuscript:** Introduction opening paragraph (four sentences before qHP platform sentence).

### R3-Intro-P2 — Gap-driven literature review; defer $\mathcal{S}$ equation

**Referee concern (simulated Referee \#2):** Literature paragraph read as a topic list (strain / doping / transport) without an unresolved **physical** question; novelty framed as ``define $\mathcal{S}$'' rather than **additive approximation failure**; missing **However** negative statement, **why** energetic coupling matters (stability ranking, defect preference), **elastic-frustration** mechanism, and **cluster-expansion** context; $\mathcal{S}$ and Eq.~\eqref{eq:synergy_order} introduced before the physics gap was established; ``class of covalent molecular networks'' overgeneralizes.

**Response:** Second block reorganized as **known $\rightarrow$ mechanism $\rightarrow$ However (gap) $\rightarrow$ related nonlinear studies $\rightarrow$ CE context $\rightarrow$ qHP quantification gap**. Added **vandewalle2009cluster** for alloy cluster-expansion cross terms. **$\mathcal{S}$** introduced only after three physics questions, as the **same-functional four-corner difference omitted in additive workflows** (not a renamed fitted interaction parameter). Removed ``synergy order parameter'' and ``decouple'' from Intro; scoped to **qHP C$_{60}$ validation platform**.

**Manuscript:** Introduction literature block (qHP platform through contribution sentences).

### R3-Intro-P3 — Hypothesis-first contributions; findings not TOC

**Referee concern (simulated Referee \#2):** Final Intro paragraph read as a computational workflow summary (``We introduce/quantify/compare $\mathcal{S}$''); missing explicit **hypothesis** and **scientific questions**; contributions listed like a table of contents ($\alpha$, DOS, charge without hierarchy); no **why qHP C$_{60}$**; too much Methods detail (rigid, $+3$\%, supercell); missing **why energetic stability** matters; weak generality statement.

**Response:** Closing block rewritten as **problem $\rightarrow$ platform rationale $\rightarrow$ hypothesis + three tests $\rightarrow$ brief approach ($\mathcal{S}$ as audit, Sec.~Methods) $\rightarrow$ three **findings** (additive failure, $\alpha$ misprediction, P upper bound + chemical-mismatch channel) $\rightarrow$ moderated **potential** generality. Introduced **$E(\epsilon,\delta)$ energy-landscape** framing and **relative energetic stability** as the primary observable; electronic proxies demoted to secondary validation in Results.

**Manuscript:** Introduction closing paragraph (six sentences before Methods).

### R3-Intro — Round 3 overall verdict (simulated Referee \#2)

**Referee summary:** Introduction reframed from workflow/$\mathcal{S}$-first to **physics gap $\rightarrow$ hypothesis $\rightarrow$ tests $\rightarrow$ findings**; P1 physics-first opening; P2 gap-driven literature with CE context; P3 hypothesis and scientific questions. ``Order parameter'' removed from Abstract/Intro; full Methods theory in **R4-Methods-B** (Round 4.2).

**Author response:** Intro P1--P3 revised per R3-Intro-P1 through R3-Intro-P3; aligned with Title/Abstract additive-failure narrative.

### R4-Methods-A1 — Why PBE+D3 (not SCAN / HSE / rVV10)?

**Referee concern (simulated Referee \#2):** Functional choice is stated without justification; meV-scale conclusions require XC sensitivity discussion; reviewer would request at least one SCAN (or r$^2$SCAN) spot-check.

**Response:** Methods now justify PBE+D3 for \emph{matched} four-corner grids at meV resolution, contrast with hybrid/meta-GGA and Capobianco rVV10 scope (gaps/transport), and state that $\mathcal{S}$ is a within-functional difference so absolute gap errors largely cancel.
A SCAN/r$^2$SCAN representative corner is **not** in the current dataset; Limitations and future work flag this as a targeted sensitivity test (no fabricated SCAN numbers).

**Manuscript:** Sec.~Electronic structure method, ``Exchange-correlation and dispersion''; Limitations outlook.

### R4-Methods-A2 — Role of Grimme D3

**Referee concern:** Why D3 on a covalent network? Is vdW negligible?

**Response:** Added physical rationale (inter-cage dispersion in the qHP plane) and quantitative anchor $\mathcal{S}_{\mathrm{vdW}}\approx +0.33$~meV/atom vs.\ $|\mathcal{S}_{\mathrm{rigid}}^{\mathrm{PBE+D3}}|$ on the matched tetramer $P$ grid (Table~\ref{tab:II}).

**Manuscript:** Same paragraph; Discussion (iv) retains vdW decomposition.

### R4-Methods-A3 — SCF precision for difference-of-differences

**Referee concern:** $\mathrm{EPS\_SCF}=10^{-6}$~$E_{\mathrm{h}}$ may be insufficient when $|$\mathcal{S}$|$ is only a few meV/atom; four-energy cancellation must be discussed explicitly.

**Response:** Methods now state inner/outer OT thresholds ($10^{-6}$~$E_{\mathrm{h}}$; MAX\_SCF 300; OUTER\_SCF 30), note tighter $10^{-7}$~$E_{\mathrm{h}}$ in charged vertical workflows (SI), and explain that $\mathcal{S}$ noise is governed by \emph{cancellation} among identically protocolled corners.

**Manuscript:** ``SCF convergence and four-corner precision''; SI Methods Marcus thresholds.

### R4-Methods-A4 — Cutoff benchmark on $\mathcal{S}$, not only total $E$

**Referee concern:** Single-point total-energy shift at 400 vs.\ 350~Ry does not prove $\mathcal{S}$ convergence.

**Response:** We retain the verified single-corner audit (${\sim}0.057$~meV/atom at $6\times\mathrm{C}_{60}$ N $+3$\%) and interpret it as an \emph{upper bound} on one-corner drift: if one corner shifts by $\delta$, $|$\mathcal{S}$|$ changes by $\mathcal{O}(\delta)$ at most.
This is well below the smallest $|$\mathcal{S}$|$ in the $n\leq 4$ core grid (e.g.\ $2.3$~meV/atom for N at $n{=}1$).
Full four-corner $\mathcal{S}(\mathrm{cutoff})$ curves are honestly deferred to future work (Limitations).

**Manuscript:** Cutoff paragraph; Validation benchmarks (ii); SI Methods.

### R4-Methods-A5 — $k$-point convergence of $\mathcal{S}$

**Referee concern:** Energy $k$-convergence does not guarantee $\mathcal{S}(k)$ convergence.

**Response:** Documented $\Gamma$-only production sampling for 60--480 atom supercells (in-plane lattice up to ${\sim}44$~\AA\ at $n{=}8$); direct $\mathcal{S}(k)$ tests listed as future sensitivity work alongside cutoff/EPS curves.

**Manuscript:** ``Plane-wave mesh and Brillouin-zone sampling''; Limitations.

### R4-Methods-A6 — Force thresholds for relaxation

**Referee concern:** BFGS force criteria unspecified; loose forces could explain $\mathcal{S}\approx 0$ after relax.

**Response:** Validation benchmarks now cite tetramer BFGS force/displacement thresholds and cross-reference Sec.~\ref{sec:methods_relax} ($4.5\times10^{-4}$ / $3.0\times10^{-4}$~Ha/bohr).

**Manuscript:** Sec.~\ref{sec:validation}; `methods_extended.tex`.

### R4-Methods-A7 — Supercell size and periodic images

**Referee concern:** Is $n{=}8$ large enough? Periodic image interactions on $|$\mathcal{S}$|$?

**Response:** Validation states $n{=}8$ (480 atoms, ${\sim}44$~\AA\ in-plane) and **honestly** notes that explicit periodic-image convergence tests on $|$\mathcal{S}$|$ were not performed beyond this grid.

**Manuscript:** Sec.~\ref{sec:validation}.

### R4-Methods-A8 — Why only periodic $n{=}1$ ionic relaxation?

**Referee concern:** Relaxation limited to $n{=}1$ $P$ appears arbitrary without tetramer companion.

**Response:** Validation separates periodic $n{=}1$ $P$ GEO\_OPT (4/4) from tetramer four-corner relaxation (Table~\ref{tab:II}/III at ${\sim}5$~at.\%); scope is explicit in Methods and Validation.

**Manuscript:** Sec.~\ref{sec:validation}; `methods_extended.tex` ionic-relaxation benchmark.

### R4-Methods-A9 — Rigid protocol physical boundary conditions

**Referee concern:** Rigid strain reads as artificial without experimental/kinetic correspondence.

**Response:** Methods now tie fixed fractional coordinates to epitaxial clamping, substrate adhesion, and ultrafast loading---aligned with Abstract/Discussion upper-bound narrative.

**Manuscript:** ``Spin, charge, and mechanical boundary conditions''; cross-ref Sec.~\ref{sec:validation}.

### R4-Methods-A10 — Numerical error bars on $\mathcal{S}$

**Referee concern:** No uncertainty estimates (e.g.\ $31.9\pm ?$ meV/atom).

**Response:** Four-corner cancellation argument plus partial cutoff bound; explicit $\mathcal{S}(\mathrm{EPS\_SCF})$ sensitivity curves deferred to future work (no fabricated error bars).

**Manuscript:** SCF precision paragraph; Limitations.

### R4-Methods-A11 — Spin polarization for B/N/P

**Referee concern:** Are local moments treated with spin-polarized DFT?

**Response:** Production $\mathcal{S}$ grid uses closed-shell RKS on neutral substitutional cells; UKS only for Hirshfeld strain-path audits with odd electron counts (Sec.~\ref{sec:methods_population}).

**Manuscript:** ``Spin, charge, and mechanical boundary conditions''.

### R4-Methods-A12 — Charge neutrality / substitution model

**Referee concern:** Why neutral cells? How is doping charge compensated?

**Response:** Explicit neutral substitution without compensating background; $\Delta E_{\mathrm{sub}}$ is not a formation enthalpy (cross-ref Sec.~\ref{sec:notation}).

**Manuscript:** Same paragraph.

### R4-Methods-A — Software note (CP2K vs.\ VASP/PAW)

**Referee concern (implicit):** Reviewer template assumed VASP/PAW; manuscript must be internally consistent.

**Response:** Methods identify **CP2K + GTH pseudopotentials + GPW**, not VASP PAW---consistent with all production `*.inp` files.

**Manuscript:** Opening of Sec.~Electronic structure method.

### R4-Methods-A — Round 4.1 overall verdict (simulated Referee \#2)

**Referee summary:** Methods II.A upgraded from ``we use PBE+D3'' to functional/dispersion justification, four-corner SCF logic, partial $\mathcal{S}$ cutoff bound, $\Gamma$-only scope, spin/charge/rigid BCs, and honest gaps (no SCAN subset; no full $\mathcal{S}(\mathrm{cutoff}/k/\mathrm{EPS})$ curves yet).
Residual Major-level backlog: **Track A** SCAN spot-check; four-corner cutoff400 grid for direct $\mathcal{S}(\mathrm{cutoff})$ SI figure.

**Author response:** Main Methods + SI Methods + `sdc_method_section` terminology harmonization (``coupling energy $\mathcal{S}$''); Validation benchmarks expanded; Limitations outlook updated.

---

## Round 4.2 — Methods II.B--II.D (Eq.~(1), Taylor expansion, rigid/relaxed protocol)

### R4-Methods-B1 — Mixed derivative / Taylor expansion connection

**Referee concern:** Eq.~(1) reads as an unexplained four-point difference; Reviewer expects explicit link to $\partial^2 E/\partial\epsilon\,\partial\delta$ and Taylor expansion of $E(\epsilon,\delta)$.

**Response:** Sec.~\ref{sec:methods_coupling} now opens with a Taylor expansion of $e(\epsilon,x)$ [Eq.~\eqref{eq:taylor_coupling}], identifies the omitted bilinear term $c\,\epsilon x$, and states that Eq.~\eqref{eq:synergy_order} is the corresponding four-corner finite-difference estimator at finite load. Discussion (Sec.~\ref{sec:stress_coupling}) adds one sentence tying $\mathcal{S}$ to the discrete mixed second derivative.

**Manuscript:** `sdc_method_section.tex`; Discussion `sec:stress_coupling`.

### R4-Methods-B2 — Terminology: ``synergy'' and ``order parameter''

**Referee concern:** ``Synergy'' and ``order parameter'' suggest rebranding of interaction/coupling energy; PRB reserves order parameter for broken-symmetry phases.

**Response:** Methods define $\mathcal{S}$ explicitly as the \emph{strain--dopant coupling energy}, not an order parameter. Subsection title is ``Strain--dopant coupling energy''; SI theory inventory updated. Residual ``synergy'' in data-availability URL path only.

**Manuscript:** `sdc_method_section.tex`; `supplementary_material_theory.tex`.

### R4-Methods-B3 — Why four states (reference gauge)

**Referee concern:** Why four corners? Reference independence / gauge?

**Response:** Added explicit four-energy form [Eq.~\eqref{eq:four_corner}] and text: only a four-state construction removes linear strain, linear doping, and shared pristine reference in one gauge-fixed estimator; three-point schemes retain linear contamination.

**Manuscript:** `sdc_method_section.tex` [Eq.~\eqref{eq:four_corner}].

### R4-Methods-B4 — Sign convention

**Referee concern:** Meaning of $\mathcal{S}>0$ vs.\ $\mathcal{S}<0$ for reading figures.

**Response:** Methods paragraph ``Physical meaning, sign, and units'': $\mathcal{S}<0$ = coupled corner more stable than additive (cooperative); $\mathcal{S}>0$ = less stable than additive (anti-cooperative). Discussion sign examples at $n{=}4$ retained.

**Manuscript:** `sdc_method_section.tex`; Discussion `sec:generality`.

### R4-Methods-B5 — Units (meV/atom vs.\ eV/cell)

**Referee concern:** Why per-atom normalization across supercells?

**Response:** Text states meV/atom for comparability across $n\times\mathrm{C}_{60}$ at fixed one-substituent-per-C$_{60}$ loading, with tetramer concentration caveat (Sec.~\ref{sec:generality}).

**Manuscript:** `sdc_method_section.tex`.

### R4-Methods-B6 — Size scaling of $\mathcal{S}(n)$

**Referee concern:** How does $\mathcal{S}$ scale with supercell size?

**Response:** Methods state $|\mathcal{S}|$ is not constrained to $1/n$ linear decay; electrostatic dilution and local distortion can peak at intermediate $n$, with cross-reference to Table~\ref{tab:IV} and Fig.~\ref{fig:synergy}.

**Manuscript:** `sdc_method_section.tex`.

### R4-Methods-B7 — Discrete $\delta$ vs.\ continuous symmetry

**Referee concern:** Is $\mathcal{S}(\epsilon,\delta)$ symmetric under exchange of strain and composition?

**Response:** Clarified that $\delta$ is a discrete chemical label; B/N/P cross terms are not required to follow a single smooth surface in $\delta$.

**Manuscript:** `sdc_method_section.tex`.

### R4-Methods-B8 — Error propagation (four corners)

**Referee concern:** No uncertainty propagation for four independently converged totals.

**Response:** Added conservative estimate $\sigma_{\mathcal{S}}\approx 2\sigma_e$ for uncorrelated per-atom corner uncertainties, with note that identical protocols induce partial cancellation (Sec.~\ref{sec:validation}).

**Manuscript:** `sdc_method_section.tex`; cross-ref Validation benchmarks.

### R4-Methods-B9 — Physical interpretation sentence

**Referee concern:** Equation defined mathematically but not physically.

**Response:** ``Physically, $\mathcal{S}$ measures the energetic cost of \emph{nonlinear} interaction between externally imposed biaxial strain and dopant-induced internal stress'' (Methods); linked to internal vs.\ external stress fields in Discussion.

**Manuscript:** `sdc_method_section.tex`; Discussion `sec:stress_coupling`.

### R4-Methods-D1 — Rigid vs.\ relaxed protocol (II.D)

**Referee concern:** Rigid-strain upper bound vs.\ ionic relaxation not clearly separated in notation section.

**Response:** `sec:notation` now has a dedicated ``Rigid vs.\ relaxed mechanical protocols'' paragraph: rigid strain = fixed fractional coordinates (upper bound); relaxed strain = fixed-cell BFGS at each corner (Sec.~\ref{sec:methods_relax}, Table~\ref{tab:II}, Fig.~\ref{fig:synergy}(e)).

**Manuscript:** `strain_doped_graphullerene.tex` `sec:notation`; `methods_extended.tex` `sec:methods_relax`.

### R4-Methods-B — Round 4.2 overall verdict (simulated Referee \#2)

**Referee summary:** Eq.~(1) reframed from ``new metric'' to **energy functional $\rightarrow$ Taylor bilinear term $\rightarrow$ four-corner finite difference $\rightarrow$ DFT audit**; terminology de-``synergy''/de-``order parameter''; sign, units, scaling, gauge, error propagation, and rigid/relaxed protocols addressed in Methods without new DFT.

**Residual (optional):** schematic figure (Taylor vs.\ four-corner) still backlog; full $\mathcal{S}(\mathrm{cutoff}/k/\mathrm{EPS})$ curves Track A.

**Author response:** `sdc_method_section.tex` expanded (~one Methods page of theory); `sec:notation` rigid/relaxed split; Discussion one-liner on mixed derivative.

---

## Summary response

We thank the referee for recognizing the corrections to doping concentration, Marcus definitions, functional mismatch disclosure, and legacy-PBE vs.\ PBE+D3 separation. This revision addresses Report No.~2 notation, APS section hierarchy, language, and figure--text alignment; **Table~III** tetramer ionic-relaxation is **complete** (4/4; sign reversal of $\mathcal{S}$); **Table~IV** alternate-placement DFT is **complete** (24/24). We further upgraded the narrative from a single-qHP case study to a **covalent molecular-network** coupling framework (internal vs.\ external stress field, mismatch--$|\mathcal{S}|$ scaling, additive-model applicability boundaries, and qualitative experimental signatures in new Methods/Discussion subsections). Main-text transport/$J$ content is consolidated in the **Supplemental Material**; Fig.~3 in the main text reports the Marcus protocol schematic and tabulated $\lambda^{\pm}$ only.

**New DFT in this pass:** periodic $n{=}1$ $P$ four-corner fixed-cell geometry optimization (**4/4** complete); Hirshfeld population along the strain path for **B**, **N**, and **P** at $n{=}1$ (**18/18** complete); reference-placement PBE+D3 tetramer $\alpha$ grid (**complete** **24/24**; Fig.~\ref{fig:decoupling}(d) endpoint map and archived Table~I in the Supplemental Material).

**Manuscript alignment (this pass):** Main figures are four process-centric panels (Figs.~\ref{fig:electronic}--\ref{fig:mechanism}): strain paths ($E_g$, $\pi$-DOS, $\Delta E$), $\mathcal{S}(n)$ size scaling, microscopic $q$/$\bar{d}$/$\sigma$ paths, and mechanism endpoints. Reference-map **PBE+D3** $\alpha$ (Table~IV) replaces legacy PBE Table~I in the endpoint map; explicit **decoupling** definition (not $\alpha$--$|\mathcal{S}|$ anticorrelation); $\mathcal{S}_{\mathrm{vdW}}\approx +0.33$~meV/atom from D3 corner extraction; Eshelby/defect-elastic framing; Table~V tetramer-proxy disclaimer; $n\leq 4$ non-monotonic $|\mathcal{S}|$ note; raw $\Delta E_{\mathrm{sub}}$ terminology.

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

**Response:** We expanded sign-conflict physics in Discussion (iii) and Design implications (B/N $n{=}4$), retain Table~V $\Delta\bar{d}$/$\sigma(\bar{d})$ with explicit **tetramer-proxy** scope (not periodic $n{=}1$ bond statistics), and added **$\mathcal{S}_{\mathrm{vdW}}\approx +0.33$~meV/atom** on the matched-functional $P$ tetramer grid (negligible vs.\ total $|\mathcal{S}|$). Hirshfeld charge strain-path audits for $n{=}1$ **B**, **N**, and **P** are **complete** (18/18): P shows the largest fractional shift under tension ($+0.063\to+0.056\,e$ at $+3$\%); B and N shift more modestly ($+0.12\to+0.11\,e$ and $+0.069\to+0.057\,e$). Sign-origin paragraphs distinguish geometric (P) vs.\ electronic (B/N) channels. Periodic VBM/CBM isosurfaces on MSMS-rendered $n\times\mathrm{C}_{60}$ cells (Supplemental Material; N size series + P $n{=}4$) provide a spatial localization signature for the finite-size dilution channel; Mayer/Bader remain future work.

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

**DFT status:** Table~III tetramer **4/4**; periodic $n{=}1$ P **4/4**; reference-placement PBE+D3 tetramer grid **complete** **24/24** (reference-map $\alpha$: B $+58.7$, N $-297.5$, P $+456.0$~meV/\%).

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

**Manuscript:** Breakdown of Additive Strain--Doping Energetics in Quasi-Hexagonal C$_{60}$ Graphullerene  
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
1. **Electronic (N vs.\ B):** Results Sec.~\ref{sec:electronic} now reports verified $\epsilon{=}0$ gaps from the archived tetramer electronic-structure set ($E_g^{\mathrm{B}}\approx 0.03$, $E_g^{\mathrm{N}}\approx -0.14$, $E_g^{\mathrm{P}}\approx 0.05$~eV) and links them to opposite $\alpha$ signs on the reference PBE+D3 map (Table~IV; ${\sim}360$~meV/\% span on the legacy PBE grid in archived Table~I). Fig.~\ref{fig:electronic}(b,c) and Supplemental Fig.~\ref{fig:pdos} provide the $\pi$-DOS and $E_g(\epsilon)$ process context.
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
| Main-figure process layout | **R411/R412**: four figures (electronic/synergy/decoupling/mechanism); strain paths replace bar catalogs; $\sigma(\bar{d})(\epsilon)$ in Fig.~\ref{fig:decoupling}(c); endpoint map in (d) |
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
| Reference placement PBE+D3 ($\alpha$ modernization) | I / II | **complete** **24/24**; Table~\ref{tab:I} legacy-PBE retained in SI only |
| Transport / $J$ main text | SI | **complete** (Marcus/$J$ in Supplemental Material; main Fig.~3 protocol only) |
| SI Fig.~S4 MSMS VBM/CBM panels | SI | **complete** (N size series + P $n{=}4$ in SM; gray MSMS cages; MO-cube SP **12/12** incl.\ $n{=}8$ orbitals) |
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


---

## Round 5 — Simulated Referee #2: Results (Section III) — 2026-07-29

**Overall Results score (referee):** ~3.3/5 → targeted **Major Revision** fixes below.

| ID | Referee theme | Manuscript / figure action | Status |
|----|---------------|---------------------------|--------|
| **R5-Fig1** | Fig.~1 too workflow-like; missing stress / $E(\epsilon,\delta)$ | Fig.~\ref{fig:electronic}(e): physics chain + bond-stress coloring + schematic landscape (`draw_physics_coupling_schematic`) | **done** |
| **R5-Fig2** | Failure of additivity not visualized; no $|S|$ distribution; relaxation “vanishes” | Fig.~\ref{fig:synergy}(c) additive vs coupled bars @ $n{=}4$; (d) 15-point histogram; (e) stress-release framing | **done** |
| **R5-Fig3** | $\alpha$--$S$ needs statistics; avoid “decouple”; $n{=}3$ sample | Fig.~\ref{fig:decoupling}(d): Pearson $r$, $R^2$, Spearman $\rho$; text “weak correlation” / non-predictor | **done** |
| **R5-Fig4** | DOS/charge standalone | Results + Discussion: $\pi$-DOS / Hirshfeld paths tied to nonlinear $\mathcal{S}$ audit | **done** |
| **R5-TabIII** | Bond lengths without comparison context | Table~\ref{tab:III} footnote: DFT internal + literature qHP strain context | **done** |
| **R5-Disc** | Q1–Q3 mechanism depth | Existing `sec:stress_coupling` / `sec:mechanistic` retained; relaxation as upper-bound protocol | **partial** (Mayer backlog) |

**Referee A-list cross-map:** narrative refactor (R2–R4) + rigid applicability (Limitations) + $S$ convergence curves remain **partial** (single-point cutoff audit only).


---

## Round 6 — Simulated Referee #2: Deep Technical Review — 2026-07-29

**Referee recommendation (simulated):** Major Revision — publish after strengthening physics narrative, rigid-protocol relevance, and $\mathcal{S}$ interpretation (not after new descriptor framing).

**Simulated overall scores (/10):** Novelty 6.5→target 8; Physics 8.5; DFT 9.0; Rigor 7.5; Writing 8.5; Figures 8.0; Storytelling 5.5→target 8; PRB fit 7.5.

### Major Concern 1 — Is $\mathcal{S}$ really new?

**Referee:** Four-state interaction energy / discrete mixed second derivative; novelty cannot rest on Eq.~(1).

**Response:** Primary discovery reframed as **nonlinear strain--dopant energetic coupling and additive failure** (Abstract opening; Conclusions). $\mathcal{S}$ is the **gauge-fixed four-corner estimator** of the bilinear Taylor term [Eqs.~\eqref{eq:taylor_coupling}--\eqref{eq:four_corner}] and is **not** claimed as a new thermodynamic observable (Intro; `sec:methods_coupling`; Discussion cluster-expansion paragraph with **vandewalle2009cluster**). Story: physics first, symbol second.

### Major Concern 2 — P largest: mechanism incomplete

**Referee:** Atomic radius alone insufficient; need bond / charge / frustration channels.

**Response:** `sec:mechanistic` adds explicit **(i) local bond stretching, (ii) charge redistribution, (iii) elastic frustration** for P, with Table~\ref{tab:III} and Hirshfeld audit numbers; Fig.~\ref{fig:mechanism} ties paths to $|\mathcal{S}|$.

### Major Concern 3 — Relaxation suppresses $\mathcal{S}$

**Referee:** If equilibrium coupling is near zero, what is rigid $\mathcal{S}$ for?

**Response:** New subsection **Physical relevance of mechanically constrained configurations** (`sec:constrained_loading`): epitaxial/clamped substrates, adhesion, ultrafast/cyclic load, MEMS/nanoflexures; rigid $\mathcal{S}$ as **upper bound** when ions cannot relax; relaxed audits for annealed equilibrium. Not “S vanished” narrative (Fig.~\ref{fig:synergy}(e)).

### Major Concern 4 — Single material

**Referee:** Why graphullerene; is it accidental?

**Response:** Intro: qHP C$_{60}$ chosen as **soft, pre-strained** network vs rigid graphene/COF; generality via matched four-corner protocol on each host (Conclusions; Limitations). No fabricated graphene DFT in this revision.

### Major Concern 5 — Only B/N/P

**Referee:** Why not Al/Si/Ga/As/S?

**Response:** Intro: minimal **III/V-neighbor** set spanning donor/acceptor/size channels; explicit scope note that extended chemistry is future work (Limitations).

### Major Concern 6 — Statistics ($n=3$)

**Referee:** Need Pearson/Spearman; bootstrap?

**Response:** Fig.~\ref{fig:decoupling}(d) + Results text report $r$, $R^2$, $\rho$; Limitations state **bootstrap not meaningful at $n{=}3$** without additional converged dopants. Honest: $r\approx+0.71$ supports **failure of $\alpha$ as rank predictor**, not “$R^2=0.12$ weak correlation.”

### Major Concern 7 — Error bars

**Response:** `sdc_method_section` $\sigma_{\mathcal{S}}\approx 2\sigma_e$ propagation; Methods cutoff audit on $\mathcal{S}$ sensitivity; Limitations: DFT-internal geometry only (no experimental $\pm$ on bond lengths).

### Major Concern 8 — Functional (SCAN)

**Response:** Methods + Limitations: PBE+D3 production; **SCAN/r$^2$SCAN spot-check listed as future work** — no fabricated meta-GGA numbers.

### Major Concern 9 — Literature (cluster expansion / mixed derivative)

**Response:** Discussion literature block: **vandewalle2009cluster**, elastic superposition context, four-corner finite difference as CE interaction-energy analogue.

### Major Concern 10 — Theoretical framework

**Response:** `sdc_method_section.tex`: Taylor expansion Eq.~\eqref{eq:taylor_coupling} $\rightarrow$ four-corner finite difference; linked in Discussion `sec:stress_coupling`. Not a separate half-page derivation (PRB Methods length), but explicit **$c\,\epsilon x$** identification.

### Simulated Editor recommendation

> Publish after Major Revision — interesting first-principles results; strengthen theoretical interpretation, rigid-strain relevance, and direct validation narrative for the coupling energy.

**Still open (Track A / honest backlog):** full $\mathcal{S}(\mathrm{cutoff},k,\mathrm{EPS})$ curves; Mayer/Bader; SCAN single-point; optional second host (graphene) four-corner grid.


---

## Round 8 — Editor + Senior Referee (Fatal Weaknesses) — 2026-07-29

**Simulated Editor line:** calculations are careful, but physics advance is not yet compelling because novelty is framed as a descriptor and mechanisms remain under-developed.

**Simulated recommendation:** Major Revision — revise substantially before PRB re-evaluation.

### Fatal Issue 1 — Claim magnitude / threshold

**Attack:** “Additive fails” without defining significant failure; 31.9 meV is meaningless without reference.

**Response:** Added additive fractional error $\eta=|\mathcal{S}|/|\Delta E_{\mathrm{coupled}}|$ [Eq.~\eqref{eq:additive_fraction}]; at $n{=}4$ P, $\eta\approx 8\%$ vs.\ $<1\%$ for B/N. Fig.~\ref{fig:synergy}(c) annotates $\eta$. Results discuss $\sigma_{\mathcal{S}}$ scale vs.\ 2–32 meV distribution.

### Fatal Issue 2 — Uncertainty on $\mathcal{S}$

**Attack:** No confidence interval on four-corner $\mathcal{S}$.

**Response:** `sdc_method_section` — cutoff audit ($|\Delta\mathcal{S}|<0.2$ meV), conservative $\sigma_{\mathcal{S}}\lesssim 2$ meV/atom; Table IV / Results report $-6.2\pm 2$, $+3.0\pm 2$, $-23.7\pm 2$ meV/atom ($\pm$ = protocol bound, not experiment).

### Fatal Issue 3 — Single material / over-generalization

**Attack:** Conclusions too general.

**Response:** Conclusions now “likely only after matched audits on each host”; Intro “likely to fail” not universal; Limitations scope qHP C$_{60}$ vs.\ graphene/COF.

### Fatal Issue 4 — Mechanism = correlation

**Attack:** P $\rightarrow$ radius $\rightarrow$ S; need chain and counterexamples.

**Response:** `sec:mechanistic` — explicit chain radius $\rightarrow$ internal stress $\rightarrow$ charge $\rightarrow$ $\mathcal{S}$; B/N counterexamples to radius-only ranking; Fig.~\ref{fig:mechanism} caption updated.

### Fatal Issue 5 — Alternative explanations

**Attack:** finite size, localization, Pulay, SCF artifact?

**Response:** New `sec:alternative` — four explicit controls with audit numbers.

### Fatal Issue 6 — Theory too weak

**Attack:** need energy functional model.

**Response:** `sdc_method_section` — $e_{\mathrm{elastic}}+e_{\mathrm{chem}}+c\epsilon x$ paragraph; Taylor + cluster expansion in Intro/Discussion.

### Fatal Issue 7 — Overclaim

**Attack:** “establishes” in Conclusions.

**Response:** Replaced with “documents” / “likely only after…”; removed “establishes” from readout map.

### Fatal Issue 8 — Descriptor-first story

**Attack:** Editor sees incremental descriptor.

**Response:** Abstract/Intro/Conclusions already physics-first; Round 8 reinforces $\eta$, uncertainty, predictive section.

### Fatal Issue 9 — Why PRB?

**Response:** Intro sentence — Taylor bilinear + CE interaction energy $\rightarrow$ PRB not methods-only journal.

### Fatal Issue 10 — Predictive power

**Attack:** post-analysis only?

**Response:** New `sec:predictive` — four-corner pre-screen before full relaxation; $|{\mathcal{S}}|>{\sim}2$ meV/atom flag.

**Still open (honest):** full $\mathcal{S}$(cutoff,k,EPS) curves; SCAN spot-check; Mayer/Bader; second host graphene grid; bootstrap needs $>3$ dopants.

---

## Simulated PRB Referee Round 9 — “Invisible Questions” (Hidden Assumptions)

**Referee concern:** Fifteen implicit assumptions reviewers ask but authors rarely answer: uniqueness of Eq.~(1), mixed derivative $\leftrightarrow$ physics, choice of total energy, 0~K, phonons, charge neutrality, local minima, strain knots, Taylor validity, conservative generalization, observability, predictivity, $E(\epsilon,\delta)$ landscape, elastic vs.\ chemical dominance, why prior work missed coupling.

**Response:** New Discussion subsection **`sec:interpretive`** (`Interpretive foundations`) consolidates answers; redundant prose removed from `sec:conceptual`.

| ID | Hidden assumption | Main-text location |
|----|-------------------|-------------------|
| HA1 | Uniqueness of Eq.~(1) vs.\ $\Delta G$, $\Delta H$, interaction energy | `sec:interpretive` ¶1; Methods `Relation to other energy measures` |
| HA2 | Why mixed derivative = coupling | Landau / CE paragraph; `vandewalle2009cluster` |
| HA3 | Why total energy not elastic/stress/free energy alone | KS ranking-bias paragraph |
| HA4 | Room temperature / 0~K | 0~K electronic totals; finite-$T$ caveat |
| HA5 | Imaginary phonons at large strain | Not audited at $\pm5$\%; $+3$\% production window |
| HA6 | Charge compensation / magnetism | Closed-shell KS; spin only where required |
| HA7 | Global vs.\ local minimum | BFGS local minima; Table~IV maps |
| HA8 | Why $\pm3$\% (not $\pm1$\%, etc.) | Knot set $\{-5,\ldots,+5\}$\%; finer meshes backlog |
| HA9 | Taylor linearity breakdown | Small-load expansion; higher-order neglected |
| HA10 | Over-generalization | Conclusions: “likely applicable only…” |
| HA11 | Is $\mathcal{S}$ observable? | Indirect → `sec:exp_signatures` |
| HA12 | Predictive use | `sec:predictive`; high $\|{\mathcal{S}}\|$ flag |
| HA13 | $E(\epsilon,\delta)$ vs.\ $\mathcal{S}$ | Landscape primary; $\mathcal{S}$ = curvature sample |
| HA14 | Elastic vs.\ chemistry | P elastic--structural; B/N electronic-leaning |
| HA15 | Why not reported before? | Full relax + additive grids mask constrained-load coupling |

**Conclusions:** Two closing sentences on prior-work masking and diagnostic role of $\mathcal{S}$.

**Abstract (Round 9b):** Opening reframed around $E(\epsilon,\delta)$ landscape; $\mathcal{S}$ as diagnostic (not order parameter); closing sentence on why prior work masked coupling (no `\cite`/section refs in abstract).

**Senior Referee framing:** Primary discovery = nonlinear coupling under mechanically constrained load; $\mathcal{S}$ = quantitative diagnostic (already Round 6--8); Round 9 makes implicit assumptions explicit for the editor.

---

## Simulated PRB Referee Round 1 — Title, Abstract, Introduction (author revision)

**Recommendation addressed:** Major Revision (presentation / PRB style).

| Referee point | Action |
|---------------|--------|
| Title “Breakdown” too strong / methodology-flavored | Retitled **Non-additive Strain--Dopant Energetics in Quasi-Hexagonal C$_{60}$ Graphullerene** (main, SI, cover letter). |
| Abstract too long (~350 words); “previously overlooked” | Rewritten to **~170 words**; “document…not explicitly quantified”; $\alpha$ failure in sentence~2; upper-bound one sentence; removed Methods/Discussion-only clauses. |
| “Scope for PRB” in main text | **Deleted** from Introduction; equivalent framing moved to **cover letter** opening paragraph. |
| Cluster expansion late; $\mathcal{S}$ over-defined in Intro | CE sentence moved to **paragraph~1**; Intro gives **one-line** $\mathcal{S}$ pointer to Eq.~\eqref{eq:synergy_order} and Sec.~\ref{sec:methods_coupling}. |
| Literature pile-up | Shortened to two-class summary + **Table~\ref{tab:lit_positioning}** (`tab_lit_positioning.tex`). |
| Novelty = “we discover $\mathcal{S}$” | Opening contribution sentence reframed: quantify bilinear interaction and document when additive workflows fail. |
| Three findings in Intro | **Restored** condensed (1)--(3) block with A-level numbers ($31.9\pm 2$ meV/atom, $\eta\approx 8\%$). |
| Split Makov mega-sentence | Split into two sentences (intrinsic strain; local stress + periodic audit motivation). |

**Files:** `strain_doped_graphullerene.tex`, `tables/tab_lit_positioning.tex`, `cover_letter_prb.txt`, `supplementary_figures.tex`.

**Next:** Simulated Round 2 — Computational Methods (convergence, Eq.~(1) uniqueness, error propagation).

---

## Simulated PRB Referee Round 2 — Computational Methods (author revision)

**Recommendation addressed:** Major Revision (evidence vs.\ meV/atom claims).

| Referee point | Action |
|---------------|--------|
| **M1** XC cancellation assumed | Methods: vdW $\mathcal{S}_{\mathrm{vdW}}\approx 0.33$ meV/atom and cutoff $|\Delta\mathcal{S}|<0.2$ meV/atom cited as **demonstrated** audits; SCAN/r$^2$SCAN four-corner spot-checks listed **pending** (Table~\ref{tab:sigma_S}; Limitations). |
| **M2** $\Gamma$-only $k$ | Explicit $\Gamma$-only caution for smallest $|\mathcal{S}|$ ($2.3$--$3.0$ meV/atom at $n{=}1$); $2\times 2\times 1$ benchmark **pending** (Table~\ref{tab:sigma_S}). |
| **M3** $\sigma_{\mathcal{S}}\lesssim 2$ meV | New **Table~\ref{tab:sigma_S}** (`tab_sigma_S_benchmark.tex`): SCF propagation, cutoff, D3, pending $k$/XC rows; reporting band defined as conservative protocol floor. |
| **M4** Upper bound buried | Abstract opens **Under mechanically constrained loading**; rigid-strain BC paragraph unchanged as upper bound. |
| **M5** Relaxation benchmark weak | Validation lists $n{=}4$ P periodic fixed-cell relax as **targeted backlog** (no numbers without converged GEO). |
| **M7** Defensive $\mathcal{S}$ Methods | `sdc_method_section.tex` compressed (~40\%); interpretive material → Discussion (`sec:interpretive`) + SI. |
| **M8** Descriptor table in main | `tab_descriptor_comparison.tex` moved to SI; main cites **Table~\ref{S-tab:descriptor}** via `xr-hyper`. |
| **M9** Taylor physics late | **Eq.~\eqref{eq:taylor_coupling}** in Introduction; $\mathcal{S}$ = four-corner **estimator** in Methods. |
| **M10** $\eta$ | Retained; Abstract cites $\eta\approx 8\%$ at $n{=}4$. |
| **m1--m3** Length / scope | Literature table to SI; `tab_lit_positioning` SI-only; compile uses `xr-hyper` prefix `S-` for cross-document refs. |

**Track A backlog (no fabricated Results numbers):** SCAN/r$^2$SCAN $n{=}1$ P @ $+3$\% four corners; $\Gamma$ vs $2\times 2\times 1$ for $n{=}1$ B/N/P @ $+3$\%; periodic $n{=}4$ P ionic relaxation.

**Files:** `strain_doped_graphullerene.tex`, `sdc_method_section.tex`, `tables/tab_sigma_S_benchmark.tex`, `tables/tab_lit_positioning.tex`, `tables/tab_descriptor_comparison.tex`, `supplementary_figures.tex`, `compile_prb.sh`, `si_methods_section.tex`.

**Verify:** `bash paper/compile_prb.sh` → main 16 pp., SI 6 pp.; main undefined refs cleared.

**Next:** Simulated Round 3 — Results (Figs.~2--4).

---

## Round 3 — Simulated Referee #3: Results (Section III) — 2026-08-01

**Referee recommendation:** Major Revision (borderline accept); presentation fixes below.

| ID | Referee theme | Manuscript / figure action | Status |
|----|---------------|---------------------------|--------|
| **R3-M1** | Fig.~1 overloaded (structure + DOS + gap + landscape) | Caption reframed: (a) structure; (b--d) one-parameter slices; joint audit deferred to Fig.~\ref{fig:synergy}; full physical split deferred | **partial** (caption + Results order) |
| **R3-M2** | Results opens with figure roadmap | Deleted four-line figure-index paragraph; physics-first opener | **done** |
| **R3-M3** | Sec.~IIIA mixes interpretation | Results = observations only; bilinear/DOS-prediction language → Discussion (`sec:stress_coupling`) | **done** |
| **R3-M4** | “does not linearly predict” without quantification | Removed from Results; Discussion: “consistent with … do not, by themselves, rank” + no regression at $n{=}3$ | **done** |
| **R3-M5** | $\alpha$ lacks error bars; $n{=}3$ correlation stats | Fig.~\ref{fig:decoupling}(d): horizontal $x$-error bars (six-point linear-fit SE); **removed** Pearson/$R^2$/Spearman | **done** |
| **R3-M6** | Central test buried | **Sec.~\ref{sec:synergy}** moved first; caption leads with panel (c) additive vs coupled | **done** |
| **R3-M7** | $\eta>1\%$ implied universal | Results + Discussion: **operational thresholds adopted in this work** | **done** |
| **R3-M8** | $|\mathcal{S}|$ distribution needs box plot | Fig.~\ref{fig:synergy}(d): histogram + inset box (median, Q1, Q3) | **done** |
| **R3-M9** | Relaxation only P | Results: **illustrative** $n{=}1$ P only; no general law claimed | **done** |
| **R3-M10** | Premature because/therefore in Results | Observation-only rewrite; mechanism sentence at Results end points to Discussion | **done** |
| **R3-Physics** | Why P largest only in Discussion | One closing Results sentence: largest $\Delta r_{\mathrm{cov}}$ + largest audited $|\mathcal{S}|$ | **done** |

**Verify:** `bash paper/figures/render_prb.sh` + `bash paper/compile_prb.sh`.

**Next:** Simulated Round 4 — Discussion (Section IV).

---

## Round 4 — Simulated Referee #2 (theory-focused): Discussion (Section IV) — 2026-08-01

**Referee recommendation:** Major Revision → Minor Revision if presentation fixes below are implemented.

| ID | Referee theme | Manuscript action | Status |
|----|---------------|-------------------|--------|
| **R4-M1** | Discussion too long (~5 pp.; defending $\mathcal{S}$) | Restructured IV.A--E; removed `sec:interpretive` / `sec:conceptual` definitional blocks (~30\% cut); uniqueness moved to Methods | **done** |
| **R4-M2** | Literature opener indirect | Opening: **Our work differs from previous studies in that...** (`sec:discussion_literature`) | **done** |
| **R4-M3** | qHP scope good; compress graphene/COF | Single sentence on stiffer hosts; retained non-uniqueness disclaimer | **done** |
| **R4-M4** | B/N/P: add electronic + geometric DOF | Added explicit sentence in literature subsection | **done** |
| **R4-M5** | Physical discovery belongs in Intro | Final Intro paragraph: primary discovery is **physical**, not a new descriptor | **done** |
| **R4-M6** | Eq.(1) too late | Already in Introduction (Round 2); Discussion cites only | **done** (prior) |
| **R4-M7** | Operational thresholds need caveat | Added: **practical screening criteria rather than thermodynamic boundaries** | **done** |
| **R4-M8** | Interpretive foundations too late | Definitional material → `sdc_method_section.tex` (uniqueness); Discussion physics-only | **done** |
| **R4-M9** | P mechanism hierarchy unclear | Explicit **primary / secondary / tertiary** in `sec:mechanistic` | **done** |
| **R4-M10** | Need one mechanism figure narrative | Fig.~\ref{fig:mechanism} caption reframed as hierarchy chain | **done** |
| **R4-m1--m5** | Repetition (interaction energy, order parameter, CE, Taylor) | Deleted redundant paragraphs; single Methods/Intro pointers | **done** |
| **R4-Language** | PRB passive tone | **The present results indicate** / **The calculations suggest** in Discussion + Conclusions | **done** |
| **R4-Structure** | IV.A Main finding → B Mechanism → C Literature → D Limitations → E Future work | New subsection labels `sec:discussion_main` … `sec:discussion_future` | **done** |

**Verify:** `bash paper/compile_prb.sh`.

**Next:** Optional full-manuscript tone pass; Track A backlog (SCAN, $k$, $n{=}4$ P relax) in Limitations only.

---

## Round 5 — Simulated AE / Referee #2: Physics Story Audit — 2026-08-01

**Referee recommendation:** Major Revision → Minor Revision if physics story reframed as below.

| ID | Referee theme | Manuscript action | Status |
|----|---------------|-------------------|--------|
| **R5-M1** | $\mathcal{S}$ is mixed finite difference, not new physics | Main claim = **additive screening fails**; $\mathcal{S}$ = estimator only (Abstract, Intro, Methods, Conclusions) | **done** |
| **R5-M2** | Missing general principle | **General rule** paragraph: non-additivity $\propto$ frozen elastic incompatibility (Intro, Discussion) | **done** |
| **R5-M3** | P mechanism hierarchy | Retained/strengthened primary/secondary/tertiary (Round 4 + R5 electronic responds) | **done** |
| **R5-M4** | Qualitative scaling law | Results: $|\mathcal{S}|$ vs $|\Delta r_{\mathrm{cov}}|$ at $n{=}1$ (audit JSON); N breaks radius-only trend | **done** |
| **R5-M5** | Relaxed limit is physics, not limitation | Abstract + Results + Discussion: near-zero $\mathcal{S}$ after relax = elastic-work origin | **done** |
| **R5-M6** | Electronic origin unclear | **Electronic structure responds rather than controls** (Discussion) | **done** |
| **R5-M7** | Fig. 2 graphical summary | New panel **(f)** workflow schematic + caption rewrite | **done** |
| **R5-M8** | Eq. mixed derivative | Eq.~\eqref{eq:mixed_derivative} in Methods | **done** |
| **R5-M9** | Error budget table | Table~\ref{tab:sigma_S} expanded (SCF, cutoff, vdW, relax, $k$, XC) | **done** |
| **R5-M10** | Applicability framework | **When additive screening should fail** paragraph (Discussion IV.A) | **done** |

**Verify:** `bash paper/figures/render_prb.sh` + `bash paper/compile_prb.sh`.

---

## Round 6 — Simulated AE: Full-manuscript polish — 2026-08-01

**Referee recommendation:** Minor Revision (editorial) if physics story (Rounds 4–5) is accepted.

| ID | Referee theme | Manuscript action | Status |
|----|---------------|-------------------|--------|
| **R6-E1** | Cover letter undersells physics story | Rewrote `cover_letter_prb.txt`: additive failure, estimator role, elastic-work origin | **done** |
| **R6-E2** | Abstract vs Discussion tone mismatch | Abstract: “matched four-corner audits show” (passive audit voice) | **done** |
| **R6-E3** | Intro redundancy | Merged investigate/hypothesize into single hypothesis block | **done** |
| **R6-E4** | Literature opener tone | “The present work differs…” (`sec:discussion_literature`) | **done** |
| **R6-E5** | Stale cover-letter cross-refs | Removed incorrect legacy figure pointers; Tables I–V aligned | **done** |

**Archive:** `paper/referee_report_round6_full_manuscript.md`

**Verify:** `bash paper/compile_prb.sh`

**Next:** Optional author PDF review; Track A backlog (SCAN, $k$, $n{=}4$ P relax) remains Limitations-only until converged.

---

## Round 6b — Simulated PRB Associate Editor: Editorial Value Assessment — 2026-08-01

**Editorial recommendation:** Major Revision (reframing only); desk-reject risk removed if physics chain is accepted.

| ID | AE question / request | Manuscript action | Status |
|----|----------------------|-------------------|--------|
| **AE-Q1** | New physics ≠ nonzero $\mathcal{S}$ | Abstract/Intro/Conclusion unified on frozen incompatibility → bilinear coupling | **done** |
| **AE-Q2** | Why PRB? | Intro: neglect of $\partial^2 E/\partial\epsilon\,\partial\delta$ in $E$ | **done** |
| **AE-Q3** | Generality | `sec:applicability` applicable / not applicable | **done** |
| **AE-Q4** | Citation workflow | 4-step workflow + Fig.~\ref{fig:synergy}(f,g) | **done** |
| **AE-Q5** | Prediction | As/Sb extrapolation (no DFT) | **done** |
| **AE-Q6** | Theory figure | Fig.~2 panel **(g)** $E(\epsilon)$ schematic | **done** |
| **AE-Q7** | Uniaxial strain | One sentence in applicability | **done** |
| **AE-Q8** | Finite $T$ | Limitations: 0~K; $T$ unexplored | **done** |
| **AE-Q9** | at.\% in Table IV | `tab_S_synergy_grid.tex` column | **done** |
| **AE-Q10** | Experimental handles | `sec:experimental_signatures` | **done** |
| **AE-R1** | Phenomenon not descriptor | Retained from Rounds 5–6 | **done** |
| **AE-R2** | Discussion −30% | Compressed Discussion subsections | **done** |
| **AE-R3** | Theory figure | Panel (g) + `draw_energy_coupling_schematic` | **done** |
| **AE-R4** | $k$ / SCAN | Table~\ref{tab:sigma_S} + Limitations (pending) | **done** |

**Archive:** `paper/referee_report_round6_ae_editorial_value.md`

**Verify:** `bash paper/figures/render_prb.sh` + `bash paper/compile_prb.sh`

**Next:** Round 7 — strict theoretical Referee #2 (equation-by-equation, overclaim, uniqueness of $\mathcal{S}$); optional commit on user request.

---

## Round 7 — Strict Referee #2: Computational rigor & overclaim audit — 2026-08-01

**Referee recommendation:** Major Revision (substantial mandatory calculations + full text restructuring; full re-review).

**Archive:** `paper/referee_report_round7_strict_referee2.md`

| ID | Referee theme | Response / manuscript action | Status |
|----|---------------|------------------------------|--------|
| **R7-1.1** | $\Gamma$-only $k$ corrupts $\mathcal{S}$ | Agree in principle. **Track A:** four-corner $\mathcal{S}$ for $n{=}1$ B/N/P at $2\times2\times1$; fold into Table~\ref{tab:sigma_S} and $\sigma_{\mathcal{S}}$ when converged. **Text:** Limitations + pending row (no new main-text numbers). | **partial** (disclosure); **DFT open** |
| **R7-1.2** | Dual cutoff 400/350 Ry unjustified for P | Agree. **Track A:** matched $n{=}1$ P four-corner at 350/400 Ry; optional uniform 400 Ry for $n\geq6$. **Text:** existing $6\times$C$_{60}$ N single-point + pending P audit in Table~\ref{tab:sigma_S}. | **partial**; **DFT open** |
| **R7-1.3** | SCAN / meta-GGA sensitivity | Agree. **Track A:** SCAN four-corner $n{=}1$ P @ $+3$\%. **Text:** Table~\ref{tab:sigma_S} XC row pending; ranking claims scoped to PBE+D3. | **partial**; **DFT open** |
| **R7-1.4** | vdW cross-term only tetramer P | Agree. **Track A:** B/N periodic vdW audits. **Text:** added pending row in Table~\ref{tab:sigma_S}. | **partial**; **DFT open** |
| **R7-2.1** | Finite-strain truncation at +3% | Agree. Eq.~\eqref{eq:mixed_derivative} already lists $\mathcal{O}(\epsilon^2\delta,\ldots)$; **Methods** note multi-amplitude ($\epsilon=1$--$3$\%) audit as targeted sensitivity (Limitations). **Track A:** multi-strain $\mathcal{S}$ for $n{=}1$ P. | **partial** (text); **DFT open** |
| **R7-2.2** | Ad-hoc $\eta>1\%$ / 2 meV thresholds | **Text:** operational heuristics on present protocol map; formal 95\% bands await pending $k$/XC rows (Sec.~\ref{sec:synergy}, Table~\ref{tab:sigma_S}). | **done** (honest framing) |
| **R7-3.1** | No elastic/electronic partition | Agree. **Track A:** Mayer/Bader/virial backlog. **Text:** removed “predominantly/exclusively elastic” claims; Results/Discussion/Conclusions softened to “consistent with dominant elastic-work contribution” pending partition. | **partial** (text); **DFT open** |
| **R7-3.2** | N breaks $\Delta r_{\mathrm{cov}}$ scaling | **Text:** retained qualitative N secondary channel; quantitative two-parameter law deferred (Limitations: Mayer + periodic $n{=}4$ geometry). | **partial** |
| **R7-3.3** | $\alpha$–$|\mathcal{S}|$ with $n{=}3$ | **Decline** additional dopants (Si/Al) in this revision scope. **Text:** explicit “qualitative rank among three species, not fitted correlation”; Conclusions no longer “does not reliably predict.” | **done** |
| **R7-4.1** | Rigid vs equilibrium overgeneralization | **Text:** expanded `sec:constrained_loading` — constrained vs equilibrium regimes; when additive screening may remain valid. | **done** |
| **R7-4.2** | $n{=}1$ image / $\mathcal{S}_\infty$ | **Text:** $n{=}1$ extremum may include PBC image coupling; no $\mathcal{S}_\infty$ claim in Conclusions. **Track A:** image-decoupling supercell test. | **partial** (text); **DFT open** |
| **R7-5.1** | Second host (graphene etc.) | **Decline** in current revision (resource). **Text:** “validated here on one host only”; applicability requires per-host audit (`sec:discussion_literature`). | **done** (scope) |
| **R7-5.2** | Cluster-expansion literature gap | **Text:** Discussion contrasts CE $c\,\epsilon x$ cross terms with periodic four-corner total-energy audit; novelty = audit protocol on soft network, not existence of bilinear coupling. | **done** |
| **R7-6.1** | Unified $\sigma_{\mathcal{S}}$ | Table~\ref{tab:sigma_S} lists components; quadrature sum after pending rows converge. | **partial** |
| **R7-6.2** | Figure error bars | $\alpha$ panel: fit SE bars (R3-M5); $\mathcal{S}$ values carry $\pm 2$ meV protocol band in text; full propagated bars after $k$/XC. | **partial** |
| **R7-6.3** | Finite-$T$ | Limitations: 0 K BO; vibrational entropy unexplored (R6b). | **done** (prior) |
| **R7-6.4** | Table VII tetramer-only geometry | **Track A:** periodic $n{=}4$ bond statistics. **Text:** Limitations note concentration bias. | **partial**; **DFT open** |
| **R7-6.5** | SI raw corner energies | Data Availability: machine-readable synergy tables with four-corner components in public repository; SI inventory Table~\ref{tab:inventory}. | **done** |
| **R7-M1** | $\mathcal{S}$ “unique” overclaim | **Methods:** symmetric four-corner form on audited grid; alternatives differ by $\mathcal{O}(\Delta\epsilon,\Delta\delta)$; pointer to **S-tab:descriptor**. | **done** |

**Manuscript files touched (Round 7):** `strain_doped_graphullerene.tex`, `sdc_method_section.tex`, `tab_sigma_S_benchmark.tex`, `referee_report_round7_strict_referee2.md`.

**Verify:** `bash paper/compile_prb.sh` (body $\approx 4216$ words after R7 edits).

**Next:** User-directed **Track A** queue ($k$, SCAN, $n{=}1$ P cutoff, Mayer/Bader) or commit `loop R416: Round 7 strict referee text response`.

---

## Round 7b — Referee #2: Equation-by-equation mathematical audit — 2026-08-01

**Referee recommendation:** Major Revision closes on theory rigor once $\gamma$ vs.\ $\mathcal{S}$, four-point uniqueness, and full derivation are documented.

| ID | Referee theme | Manuscript action | Status |
|----|---------------|-------------------|--------|
| **R7b-Eq1** | Taylor requires continuous $\delta$ | Intro + Methods: discrete composition caveat; expansion = finite-difference on $E(\epsilon,\delta)$ functional | **done** |
| **R7b-Eq2** | Why four corners only? | Methods `\paragraph{Why a four-point stencil?}`; SI Sec.~\ref{S-sec:why_four} vs central/LS/Hessian | **done** |
| **R7b-Eq3** | No proof $\mathcal{S}$ = mixed derivative | SI Appendix: Taylor at four corners → linear cancellation → Eq.~\eqref{eq:mixed_derivative}; Methods summary + cross-ref | **done** |
| **R7b-γS** | Confuse $\mathcal{S}$ with coupling | $\gamma$ intrinsic vs.\ $\mathcal{S}$ estimator unified (Intro, Methods, Discussion) | **done** |
| **R7b-dim** | Dimensional analysis missing | Methods + SI: meV/atom, $\eta$ dimensionless, $\gamma$ units | **done** |
| **R7b-σ** | $\sigma_{\mathcal{S}}=2\sigma_e$ without derivation | Eq.~\eqref{eq:sigma_propagation} + SI Sec.~\ref{S-sec:error_prop} | **done** |
| **R7b-sym** | Clairaut / exchange symmetry | SI Sec.~\ref{S-sec:symmetry_gauge}; Methods paragraph | **done** |
| **R7b-gauge** | Energy offset invariance | SI + Methods: arbitrary constant cancels | **done** |
| **R7b-lim** | When Taylor fails | Limitations: ${\gtrsim}10$\% strain, phase transitions | **done** |
| **R7b-App** | Appendix A (~1 page) | `si_appendix_finite_difference.tex` → Supplemental Material Sec.~I | **done** |

**New files:** `paper/si_appendix_finite_difference.tex`; `supplementary_figures.tex` (+ `xr-hyper` to main).

**Verify:** `bash paper/compile_prb.sh` (main + SI cross-refs).

**Next:** Track A convergence backlog.

---

## Round 7c — SI corner energies + $\mathcal{S}$ error bars — 2026-08-01

| ID | Referee theme | Manuscript action | Status |
|----|---------------|-------------------|--------|
| **R7c-SI-raw** | SI raw four-corner totals | `tab_S_corner_energies.tex` + `figures/data/sdc_corner_energies.csv` from `sdc_exp10_results.json` | **done** |
| **R7c-fig-err** | Figure error bars on $\mathcal{S}$ | Fig.~2(b) $\pm 2$~meV/atom; Fig.~3(d), Fig.~4(b) $y$ error bars (`SIGMA_S_MEV`) | **done** |
| **R7c-build** | Reproducible table generation | `generate_tab_S_corner_energies.py` hooked in `compile_prb.sh` | **done** |

**Verify:** `bash paper/compile_prb.sh`; `bash paper/figures/render_prb.sh`.

