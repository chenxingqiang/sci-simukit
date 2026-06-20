# Response to Referees — PRB Major Revision

**Manuscript:** Non-Additive Strain--Doping Coupling in Quasi-Hexagonal C$_{60}$ Graphullerene  
**Journal:** Physical Review B (Regular Article)

---

## Major Comment 1 — Rigid strain lacks relaxation validation

**Referee concern:** All $\alpha$ and $\mathcal{S}$ use fixed fractional coordinates; no relax benchmark; reported $|\mathcal{S}|$ may be an upper bound.

**Response:** We agree. The Methods now label the protocol an **upper bound** (Sec.~II, rigid-strain subsection) and contrast the archived rigid tetramer reference in Table~S3 ($\mathcal{S}=+0.96$~meV/atom) with the periodic $n{=}4$ $P$ value ($-23.7$~meV/atom), noting that sign and magnitude may change after ionic relaxation. **Table~S3** lists four fixed-cell GEO\_OPT corners (relaxed energies **pending**). Inputs are archived in the open repository; energies will populate when the validation queue runs after the charged-polaron vertical batch.

**Manuscript:** Methods (rigid-strain subsection); Validation benchmarks subsection; Table~S3; Limitations.

---

## Major Comment 2 — Single seed (42) placement

**Referee concern:** Quantitative results may be seed-specific.

**Response:** Main-text periodic $\mathcal{S}(n)$ is explicitly **seed~42** (Results, $n{=}4$ paragraph). **Table~S4** documents an alternate **seed~137** tetramer grid (18 ENERGY tasks: six strain points per B/N/P; **pending**). We do not claim placement-averaged universality until seed~137 converges.

**Manuscript:** Methods (substitutional doping); Table~S4; Results $n{=}4$ clause.

---

## Major Comment 3 — Mechanism needs quantitative support

**Referee concern:** N/B/P coupling classes are qualitative; need bond/charge metrics.

**Response:** We added **Table~S5** (mean nearest C distance, $\Delta\bar{d}$, covalent-radius excess) and cite it in Discussion mechanistic synthesis (ii). For electronic trends we cite gap-vs-strain (Fig.~1a), $\pi$-DOS (Fig.~1b), and Supplemental **Fig.~S4**. Mayer bond order / Bader analysis is **not** yet computed; Limitations now states this explicitly. Table~S5 reports geometric nearest-neighbor metrics only. Legacy illustrative $\lambda$ splits in archived theory notes are **not** in the compiled SI.

**Manuscript:** Discussion (i)--(ii); Table~S5; Fig.~S4. Broken cross-reference to non-existent SI Eq.~(S8) removed; IPR definition is inline in Methods.

---

## Major Comment 4 — Argumentation rigor

**Referee concern:** $\mathcal{S}$ vs $\alpha$ comparison mismatched; stability reordering overstated; size trends confounded by cutoff.

**Response:**
- (4.1) The $(\alpha_\delta-\alpha_0)\epsilon$ estimate is labeled a **qualitative sanity check only** (Discussion iv), not proof of nonlinearity.
- (4.2) Stability language tightened to **relative margins** among comparable $|E_{\mathrm{sub}}|$; we state B vs.\ P ranks at $\epsilon{=}0$ are **unchanged** by meV/atom $\mathcal{S}$.
- (4.3) Core claims focus on $n\leq 4$ at matched 400~Ry; $n\geq 6$ uses 350~Ry and N sign change is **excluded** from conclusions until Table~S2 cutoff400 control completes.

**Manuscript:** Discussion (iii)--(v), Design implications; Results synergy; Conclusions.

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
| $\mathcal{S}$ / $\pi$ symbols | Unified $\mathcal{S}$; $\pi$-DOS throughout |
| References sentence case | Main-text citekeys updated to APS sentence case (R212 bib sweep) |
| Fig.~1(c)--(d) legibility | $\alpha$ bar labels; compact $n{=}4$ $\mathcal{S}$ box; P max annotation |
| Discussion / Conclusions length | Context compressed; Conclusions condensed (no numeric repeat) |
| Supplemental citations | Overview + Tables S1--S5 cited; SI table order S1--S5 |
| Mayer/Bader mechanism | Limitations: not computed; Table~S5 geometry only |
| Marcus vs $\mathcal{S}$ | Discussion + Conclusion: orthogonal; verified $\lambda$ SI-only; **6/8** at revision (**R231**) |

---

## Pending at resubmission (computational)

| Task | Table | Status |
|------|-------|--------|
| Ionic relaxation GEO\_OPT | S3 | inputs ready; **pending** |
| Seed~137 ENERGY grid | S4 | 18 inp; **pending** |
| 400~Ry $n{=}6$ N SP (Exp10 40/41) | S2 | **pending** |
| Marcus vertical SP (8) | Fig.~S5 | **6/8** converged; six $\lambda^{\pm}$ channels in SI Fig.~S5; two pending |

---

*Document version: Loop R231 (2026-06-20). Align with `cover_letter_prb.txt`.*
