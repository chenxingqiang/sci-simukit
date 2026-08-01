# PRB Referee Report — Round 1: Section I (Introduction)

**Manuscript:** Non-additive Strain--Dopant Energetics in Quasi-Hexagonal C$_{60}$ Graphullerene  

**Status (author revision):** Title/Abstract/Intro edits **implemented** in `strain_doped_graphullerene.tex` (see `response_to_referees.md` § Simulated PRB Referee Round 1).
**Journal:** Physical Review B (Regular Article)  
**Report type:** Simulated external review (line-by-line, Section I only)  
**Date:** 2026-08-01  
**Recommendation:** **Major Revision**

---

## Overall Assessment

| Criterion | Rating | One-line verdict |
|-----------|--------|------------------|
| **Novelty** | ★★★★☆ | Nonlinear coupling under constrained load is interesting; $\mathcal{S}$ as diagnostic is incremental but well-scoped. |
| **Significance** | ★★★★☆ | meV/atom ranking bias matters for HT screening; qHP C$_{60}$ is a credible model host. |
| **Evidence** | ★★★☆☆ | Strong PBE+D3 grid; SCAN/meta-GGA and full $\mathcal{S}$(cutoff,$k$) curves still thin. |
| **Methodology** | ★★★★☆ | Four-corner protocol is clear; rigid vs relaxed honesty is a strength. |
| **Logic** | ★★★☆☆ | Intro front-loads findings; some claims still ahead of evidence placement. |
| **Writing** | ★★★★☆ | Condensed-matter tone improving; density still high for Intro. |

**Editor summary (one sentence):**  
The manuscript reports a potentially interesting breakdown of additive strain--doping energetics in qHP C$_{60}$ under mechanically constrained load; novelty should stay anchored on the *physical coupling* rather than the symbol $\mathcal{S}$, and the Introduction should defer quantitative findings to Results while tightening claims about prior literature.

---

## Major Comments (Section I–specific)

1. **Front-loaded Results in Introduction.** Paragraphs beginning “Here we *identify*…” and “We find that (1)…” (lines 65–71) read like a compressed Results+Conclusions section. PRB expects Intro to state questions, scope, and approach—not peak $|\mathcal{S}|=31.9$ meV/atom with $\eta$. **Move quantitative bullets to Results opening;** keep Intro to hypotheses and protocol.

2. **Literature positioning vs cluster expansion.** Sentence on configurational interaction (line 58) correctly cites `vandewalle2009cluster`, but earlier “remains lacking” (line 55, **revised in author draft**) must not imply the *concept* of composition--strain coupling is new. **Maintain explicit alloy/CE acknowledgment** before claiming novelty for graphullerene.

3. **“Identify” vs “demonstrate/document.”** “Here we *identify* nonlinear coupling” (line 65) overstates epistemic strength before Methods/Validation. Prefer **“document”** or **“show”** unless causality is established beyond total-energy differences.

4. **PRB Scope paragraph placement.** `\paragraph{Scope for Physical Review B}` (lines 61–63) is unusual meta-commentary inside the manuscript body. Content is valuable; **integrate into opening motivation** or shorten to two sentences without naming the journal in a `\paragraph` title.

5. **Hypothesis list density.** Three numbered hypotheses (line 68) plus four “We find” bullets (line 71) duplicate Abstract and Conclusions. **Collapse to two hypotheses** in Intro; drop repeated $\eta$ and relaxation numbers here.

6. **Single-host generalization.** Line 72 (“likely transferable only after…”) is appropriately conservative; ensure it is not undermined by stronger sentences in lines 52–53 (“covalent molecular networks” plural). **Scope first sentence to qHP C$_{60}$** or add “exemplified on”.

---

## Minor Comments (Section I)

1. Citation pile-up in line 57 (11 citekeys in one sentence)—split into two sentences or use “e.g.” with fewer keys.  
2. Line 59: 62-word sentence on P vs $\alpha$—break after “periodic scale.”  
3. “donor, acceptor, and size-mismatch triad” (line 69): B is acceptor-like in π counting—add “effective” or cite Table III.  
4. Cross-ref to `sec:interpretive` in Intro (line 70) is helpful but long; consider “Discussion” for readability.  
5. “high-throughput mapping” appears thrice in 20 lines—vary diction (“sequential screening workflows”).

---

## Detailed Line-by-Line Review — Section I

### Paragraph 1 (General motivation + additive workflow)

**Sentence 1**

*Original:*  
“Substitutional doping and mechanical strain are widely used strategies for tuning energetic stability and electronic structure in covalent molecular networks~\cite{Katiyar2025strain,Lv2026covalent}.”

*Issue:* None material.

*Reason:* Standard PRB opening; citations appropriate.

*Suggested rewrite:* Keep.

---

**Sentence 2**

*Original (pre-revision):*  
“…so the two perturbations need not be energetically independent…”

*Issue:* “Energetically independent” is vague; reviewers will ask for Taylor/CE language.

*Reason:* PRB condensed-matter audience expects coupling via cross terms in $F$ or $E$, not colloquial independence.

*Suggested rewrite (implemented in author draft):*  
“…so the two perturbations **can become energetically coupled through higher-order cross terms in the total-energy expansion**…”

*Status:* **Author revised.**

---

**Sentence 3 (clause 2 of same sentence)**

*Original:*  
“…the total response need not separate into strain-only and composition-only increments without a nonlinear interaction term.”

*Issue:* Minor redundancy with Sentence 2 after revision.

*Reason:* Same idea stated twice in one sentence.

*Suggested rewrite:*  
“…so that totals under joint load need not equal the sum of separate strain-only and substitution-only increments.”

---

**Sentence 4**

*Original:*  
“In many high-throughput mapping studies, strain and substitution are nevertheless evaluated in separate DFT workflows and combined additively…”

*Issue:* None.

*Reason:* Correctly states the *workflow* gap without overclaiming physics novelty.

*Suggested rewrite:* Keep; optional: “sequential high-throughput DFT workflows.”

---

### Paragraph 2 (Prior work gap + qHP host)

**Sentence 5**

*Original (pre-revision):*  
“…systematic quantification of their total-energy coupling under simultaneous load remains lacking for soft covalent fullerene hosts.”

*Issue:* **Overclaim.** Alloy theory and cluster expansions already quantify composition--strain coupling; reviewers will cite `vandewalle2009cluster` immediately.

*Reason:* Novelty is *host-specific audit protocol*, not discovery of cross terms in principle.

*Suggested rewrite (implemented in author draft):*  
“…matched four-corner quantification of their total-energy coupling under simultaneous load has **rarely been reported for fullerene-based covalent molecular networks**.”

*Status:* **Author revised.**

---

**Sentence 6**

*Original:*  
“Quasi-hexagonal (qHP) C$_{60}$ graphullerene~\cite{Yang2021two,Capobianco2024electron} concentrates the open question on an experimentally accessible covalent molecular network.”

*Issue:* “Concentrates the open question” is slightly rhetorical.

*Reason:* PRB prefers direct: “We study qHP C$_{60}$ as…”

*Suggested rewrite:*  
“We study quasi-hexagonal (qHP) C$_{60}$ graphullerene~\cite{…} as an experimentally accessible model covalent molecular network.”

---

### Paragraph 3 (Literature taxonomy + CE)

**Sentence 7**

*Original:*  
“Prior density-functional work largely falls into two classes: additive mapping studies… and reports of nonlinear strain--composition response in band edges, transport, or magnetism without matched four-corner *total-energy* audits…”

*Issue:* Long (40+ words); second class bundles heterogeneous physics.

*Reason:* Reviewer may ask you to separate transport papers from strain-engineering reviews.

*Suggested rewrite:* Split into two sentences; name Capobianco/Khan as *single-field* studies explicitly.

---

**Sentence 8**

*Original:*  
“Configurational interaction and cluster-expansion effective Hamiltonians for alloys already include explicit composition--strain cross terms~\cite{vandewalle2009cluster}, so a bilinear correction to $E(\epsilon,\delta)$ is expected in principle; what remains unresolved…”

*Issue:* **Critical honesty sentence—keep prominently.** Slightly long.

*Reason:* This sentence inoculates against “you discovered coupling” criticism.

*Suggested rewrite:* Break after “in principle”; start new sentence with “For soft graphullerene cages, what remains unresolved is…”

---

**Sentence 9 (end of para 3)**

*Original:*  
“…quantities that govern processing and defect retention rather than gap or mobility shifts alone…”

*Issue:* None—good PRB framing (stability vs spectroscopy).

*Suggested rewrite:* Keep.

---

### Paragraph 4 (Makov + P paradox)

**Sentence 10**

*Original:*  
“Ab initio models of pristine qHP networks report intrinsic intramolecular strain~\cite{Makov2023graphullerene}, so a substitutional defect imposes a local chemical-stress and bond-distortion field on a pre-strained, elastically soft cage; superposed with a global biaxial load, this elastic frustration motivates asking whether dopant-induced local stress couples nonlinearly with external strain at periodic scale, because tetramer linear coefficients $\alpha$ need not predict that coupling (phosphorus ranks weakest in $\alpha$ yet carries the largest rigid-strain upper bound among B/N/P).”

*Issue:* **One sentence does five jobs** (Makov, defect field, biaxial load, research question, P paradox). Parenthetical finding belongs in Results.

*Reason:* PRB Intro should motivate the question, not preview P ranking.

*Suggested rewrite:*  
Split into three sentences. Move “P ranks weakest in $\alpha$ yet…” to Results or Discussion stress-coupling subsection.

---

### Paragraph 5 — `\paragraph{Scope for Physical Review B}`

**Sentences 11–12**

*Original:*  
“The contribution is framed for condensed-matter readership as an emergent *mechanical--chemical* coupling phenomenon… rather than as a computational descriptor catalogue.” / “We report when that omitted cross term reaches meV-per-atom magnitudes…”

*Issue:* (i) Journal name in paragraph title is atypical; (ii) “meV-per-atom magnitudes” is Results-level.

*Reason:* Editors prefer substance over submission strategy in Intro.

*Suggested rewrite:* Merge first sentence into Paragraph 1; delete paragraph title; move meV sentence to Results significance criteria (`sec:synergy`).

---

### Paragraph 6 (Roadmap + findings — **highest risk block**)

**Sentence 13**

*Original:*  
“Here we *identify* nonlinear strain--dopant energetic coupling under joint load on qHP C$_{60}$…”

*Issue:* **Verb strength.** “Identify” implies new phenomenon; CE literature already expects bilinear terms.

*Suggested rewrite:*  
“Here we **document** nonlinear total-energy coupling under joint load on qHP C$_{60}$…”

---

**Sentence 14**

*Original:*  
“We investigate the total-energy landscape $E(\epsilon,\delta)$…”

*Issue:* None—aligns with Round 9 interpretive framing.

*Suggested rewrite:* Keep.

---

**Sentence 15**

*Original:*  
“We hypothesize that local chemical-mismatch stress couples nonlinearly…”

*Issue:* Repeats Paragraph 4.

*Suggested rewrite:* Delete or merge with Sentence 14.

---

**Sentence 16 (hypotheses i–iii)**

*Issue:* Appropriate structure but overlaps Abstract.

*Suggested rewrite:* Keep (i) and (iii); fold (ii) into Methods validation pointer.

---

**Sentence 17 (host choice + B/N/P)**

*Issue:* Dense; Table III ref in Intro is acceptable.

*Suggested rewrite:* Minor trim of duplicate “soft covalent network.”

---

**Sentence 18 ($\mathcal{S}$ definition)**

*Original:*  
“Matched four-corner total-energy audits quantify the omitted bilinear term as the strain--dopant coupling energy $\mathcal{S}$…”

*Issue:* Introducing $\mathcal{S}$ *after* hypotheses is correct order; cross-ref to `sec:interpretive` may be heavy.

*Suggested rewrite:* Keep definition; shorten clause after semicolon.

---

**Sentences 19–21 (“We find that (1)…(3)…”)**

*Issue:* **Major: Results leakage.** $31.9\pm 2$ meV/atom, $\eta\approx 8\%$, relaxation orders of magnitude—all belong in Results/Abstract, not Intro.

*Reason:* PRB desk reject risk: Intro reads as advocacy.

*Suggested rewrite:* Replace with:  
“We address these hypotheses using matched PBE+D3 four-corner audits on B/N/P tetramers and periodic $n\times\mathrm{C}_{60}$ supercells ($n=1$--$8$); quantitative thresholds and size-scaling trends are reported in Secs.~\ref{sec:results} and~\ref{sec:discussion}.”

---

**Sentence 22 (transferability)**

*Issue:* None—appropriately conservative.

*Suggested rewrite:* Keep.

---

## Section I — Recommended Revision Priority (for authors)

| Priority | Action |
|----------|--------|
| **P0** | Remove “We find that (1)–(3)” quantitative block from Intro → Results opener |
| **P0** | Soften “identify” → “document/show”; keep CE sentence 8 prominent |
| **P1** | Split sentence 10; defer P vs $\alpha$ paradox to Results |
| **P1** | Fold or retitle “Scope for PRB” paragraph |
| **P2** | Apply sentence-level trims (redundancy, citation pile-up) |

---

## Round 1 Exit Criteria (before Round 2 Methods)

- [ ] Intro contains **no** $|\mathcal{S}|$ numerics except optionally one peak value in final sentence—**prefer zero**  
- [ ] Alloy/CE cross-term acknowledged **before** any novelty claim  
- [ ] Word count Intro $\lesssim$ 600 words (current $\approx$ 750–800 estimated)  
- [ ] `referee_report_round1_intro.md` Major Comment 1 closed in tex  

---

*Next round:* **Section II (Methods)** — XC functional paragraph length, Eq. (1) nomenclature ($\mathcal{S}$ vs interaction energy vs cross term), validation vs Methods boundary.
