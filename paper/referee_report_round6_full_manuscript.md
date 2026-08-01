# Simulated Round 6 — Associate Editor: Full-Manuscript Polish

**Date:** 2026-08-01  
**Scope:** Cover letter, title-page narrative, cross-section consistency, PRB tone  
**Recommendation:** Accept after minor copy-editing if editor agrees physics story (Rounds 4–5) is now clear.

---

## AE summary

The revised manuscript now presents a coherent **physics-first** story: additive strain–dopant screening fails under constrained load; $\mathcal{S}$ is an estimator, not the discovery; relaxation suppression supports an elastic-work origin. Remaining work is editorial (cover letter, minor Intro compression, passive tone in Literature opener).

---

## Checklist

| ID | Item | Action | Status |
|----|------|--------|--------|
| **R6-E1** | Cover letter still frames “emergent coupling phenomenon” without stating failure condition | Rewrote `cover_letter_prb.txt` around additive screening failure + estimator role | **done** |
| **R6-E2** | Abstract active “we show” vs Discussion passive voice | Abstract: “matched four-corner audits show” | **done** |
| **R6-E3** | Intro redundancy (investigate + hypothesize + three hypotheses) | Merged to single hypothesis block | **done** |
| **R6-E4** | Literature “Our work differs” too promotional for PRB | → “The present work differs” | **done** |
| **R6-E5** | Stale cover-letter figure/table cross-refs | Removed incorrect Fig. 1a/b pointers; aligned with current Tables I–V | **done** |
| **R6-E6** | Title vs story | Title retained: *Non-additive Strain–Dopant Energetics* (matches failure framing) | **done** |
| **R6-E7** | Track A backlog in cover letter | SCAN / dense-$k$ / $n{=}4$ P relax listed as pending in item (5), not as completed | **done** |

---

## Verify

```bash
bash paper/compile_prb.sh
```

---

## Suggested next (optional)

- Author visual check of Fig. 2(f) workflow panel in PDF
- User-requested `git commit` when ready
- Track A: SCAN / dense-$k$ / periodic $n{=}4$ P relax (Limitations only until converged)
