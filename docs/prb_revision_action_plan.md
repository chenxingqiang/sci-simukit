# PRB 大修修改方案 — 仓库执行台账

> 对应 2026-07-03 逐句审稿清单；与 `docs/prb_review_cn_mapping.md`、`paper/response_to_referees.md` 并列。  
> **证据闸门**：无 converged `.out` 不得进主文 Results 新定量。

| ID | 优先级 | 动作摘要 | 轨道 | 状态 | 交付物 |
|----|--------|----------|------|------|--------|
| **P0-1** | P0 | 周期 $n{=}1$ P（次 $n{=}4$ B/N/P）四角 fixed-cell GO → $\mathcal{S}_{\mathrm{relaxed}}$ vs $\mathcal{S}_{\mathrm{rigid}}$ | **A** | **open** | `periodic_relax_validation/`；`tab_periodic_relax`（算后） |
| **P0-phys** | P0 | 内应力–外应变统一图像 + 能量分量归因框架 | **B** | **partial** | `sec:stress_coupling`；Methods 归因框架；全分量 DFT **open** |
| **P1-scale** | P1 | 失配度–$|\mathcal{S}|$ 两区制 + 加性适用边界 | **B** | **closed**（$n{=}1$ 审计） | `sec:generality`；`mismatch_synergy_scaling.json` |
| **P1-exp** | P1 | 实验可观测 signatures | **B** | **closed** | `sec:exp_signatures`（定性，无新定量） |
| **P1-2** | P1 | Hirshfeld 应变路径 B/N；Mayer 键级；差分电荷图 | **A**+B | **partial**（P 6/6 Hirshfeld 已入 Discussion） | `population_validation/`；算后 Fig. SI |
| **P1-3** | P1 | 四聚体 reference 网格 PBE+D3 $\alpha$ 重算 | **A** | **partial** | Table IV alternate 已 PBE+D3；reference 列仍 legacy → `seed137` 或新 grid |
| **P2-4** | P2 | 输运移出主线（方案二） | **B** | **closed** | 主文一句 → `supplementary_figures.pdf`（Marcus/$J$）；`compile_prb.sh` 编 SM |
| **P2-5** | P2 | 上界/泛函差异重复表述 ≤3 处 | **B** | **partial** | 已删 Discussion 重复段；主文仍 ~8 处「upper bound/legacy PBE」（多为表/图注必要标注） |
| **P2-6** | P2 | $n\geq 6$ 移 SI 表 | **B** | **closed** | `tab_S_synergy_grid.tex`（$n\leq 4$）+ `tab_S_synergy_grid_si.tex`；已 `generate_tab_S_synergy_grid.py` |
| **P3-7** | P3 | 花体 $\mathcal{S}$ 全文 | **B** | **closed** | `sec:notation` 明示 |
| **P3-8** | P3 | 图表协议脚注 | **B** | **partial** | `tab_I`, `tab_Sgrid`, Fig.~1 caption；周期弛豫表待 P0 |
| **P3-9** | P3 | Methods/Discussion 长句拆分 | **B** | **partial** | 本轮 Methods 运维句已删 |

## P0-1 计算队列（首选）

1. `python3 experiments/exp_10_size_scaling/periodic_relax_validation/generate_periodic_relax_inputs.py`
2. `bash experiments/exp_10_size_scaling/periodic_relax_validation/run_periodic_relax_validation.sh`
3. 收敛后 `analyze_periodic_relax_s.py` → `experiments/analysis/periodic_relax_validation.json`
4. `paper/scripts/update_tab_periodic_relax.py`（待 JSON complete）

四角（$n{=}1$ P）：`pristine` $\epsilon{=}0,+3\%$；`P` $\epsilon{=}0,+3\%$；PBE+D3，400 Ry，与 Table III BFGS 阈值一致。

## P1-3 文稿临时策略（算前）

- 核心脱钩论证：**Table IV alternate 列**（全 PBE+D3）+ periodic $\mathcal{S}$（Table II）。
- Table I 保留 legacy 归档；表注指向 Table IV matched-functional $\alpha$。

## Git

每轮闭环：`loop R{n}: prb action plan P?` + `AGENTS.md` 快照（用户要求时 commit）。
