# Non-additive Strain--Dopant Energetics in Quasi-Hexagonal C60 Graphullerene

Computational archive for a Physical Review B Regular Article (major revision).

**Authors:** Xingqiang Chen and Qixing Wang, Xiamen University  
**Contact:** xingqiang.chen@xmu.edu.cn  
**Repository:** https://github.com/chenxingqiang/sci-simukit  
**Revision:** branch `cursor/prb-resubmission-boundary-1d10`, commit `cbc4e398ca122f2ce821aee36b295ba44392b99a`

Production calculations use PBE+D3 (BJ) in CP2K. The reported quantity is the four-corner strain--substitution interaction at fixed dopant species,

$$\mathcal{S}_\delta(\epsilon)=\frac{E(\epsilon,\delta)-E(\epsilon,0)-E(0,\delta)+E(0,0)}{N_{\mathrm{atoms}}}.$$

B, N, and P are discrete chemical labels, not three points on one continuous derivative coordinate. A mixed derivative appears only after a local composition coordinate is introduced at fixed species.

The representative main-text value is the periodic $n=4$ phosphorus point, $|\mathcal{S}|=23.7\pm 2$ meV/atom at $+3\%$ biaxial tension (about twelve times the $\lesssim 2$ meV/atom reporting floor). Across the audited sizes the phosphorus cross term spans $23.7$--$31.9$ meV/atom. That scale can alter energy differences relevant to energetic screening when candidate separations are comparable to $|\mathcal{S}|$. It is not, by itself, a demonstrated ranking reversal.

Fixed-coordinate $|\mathcal{S}|$ is an upper-end estimate relative to the fully relaxed fixed-cell protocol studied here (epitaxial clamp, strong adhesion, or ultrafast load, where ions cannot follow). It is not a universal bound on every constraint manifold. Periodic $n=1$ phosphorus fixed-cell relaxation suppresses the cross term to the reporting floor. The $n=2$ and $n=8$ cells are reference-limited and are not used for size-trend claims.

In the three-substituent audit (covalent-radius mismatches of $-6$, $+7$, and $+30$ pm for N, B, and P), the clearly large deviation occurs for the largest mismatch ($+30$ pm, P). Three chemical points do not define a $20$ pm threshold.

Mayer bond orders, Bader charges, SCAN/r2SCAN, and a dense $k$-mesh are not reported and remain limitations. No mobility, band-gap device, or machine-learning performance claim is part of this manuscript.

## Manuscript

```text
paper/strain_doped_graphullerene.tex    main text
paper/supplementary_figures.tex         supplemental material
paper/response_to_referees.md           revision response (not part of the article)
paper/cover_letter_prb.txt              PRB cover letter
```

Compile the article with `bash paper/compile_prb.sh`.

## Repository layout

```text
paper/          LaTeX manuscript, figures, and tables
experiments/    CP2K inputs, workflows, and analysis JSON
c/              CP2K output parser, batch runner, and SDC analysis
src/            Python structure helpers and plot wrappers
dft_results/    archived converged outputs
AGENTS.md       internal computation and manuscript loop notes
```

## Reproduce the coupling table

```bash
cd c && make
export CP2K_DATA=/opt/homebrew/share/cp2k/data   # adjust for your install
./simukit-sdc ../experiments/exp_10_size_scaling/inputs
```

`simukit-sdc` writes the canonical synergy JSON. The Python wrapper must not overwrite that file.

## Citation

A journal DOI is not yet assigned. Until acceptance, cite the repository revision:

```bibtex
@misc{chen2026graphullereneS,
  title={Non-additive Strain--Dopant Energetics in Quasi-Hexagonal {C}$_{60}$ Graphullerene},
  author={Chen, Xingqiang and Wang, Qixing},
  year={2026},
  howpublished={GitHub},
  url={https://github.com/chenxingqiang/sci-simukit},
  note={Branch cursor/prb-resubmission-boundary-1d10, commit cbc4e398ca122f2ce821aee36b295ba44392b99a}
}
```

## License

MIT. See `LICENSE`.
