# PRB 中文审稿意见 ↔ 仓库状态映射

> **用途**：对照审稿条目、Loop C ID、证据文件与文稿锚点；**不**替代 `paper/response_to_referees.md` 正文。  
> **更新**：2026-06-25（全力 DFT 计划落地）

## Major Comments

| 中文审稿要点 | Loop C | 证据 / 脚本 | 文稿锚点 | 状态 | 下一 DFT |
|--------------|--------|---------------|----------|------|----------|
| M1 掺杂构型普适性不足；周期无多构型 | **C-M2** (tetramer + periodic) | `seed_validation_tetramer.json`（**24/24** ✅）；`periodic_placement_validation.json`（**16/16** ✅） | Table IV；Results $n{=}4$；Limitations | **closed**（tetramer **A** 24/24 / periodic **A** 16/16） | — |
| M2 离子弛豫（四隅） | **C-M1** | `relax_validation_tetramer.json` (4/4)；`periodic_relax_validation_n1_P.json` (**4/4**) | Table III；`sec:relax_checkpoint` | **closed**（tetramer + periodic $n{=}1$ P **A**） | — |
| M3 四聚体 α vs 周期 𝒮 变量混淆 | **C-M4** | 主稿 grep 无并列数值 | Discussion (v) | **closed** | — |
| M4 机理缺电子结构定量 | **C-M3** | `population_{B,N,P}_n1_strain.json` (**18/18**) | Discussion (iv)–(vi)；Limitations | **partial**（Hirshfeld **A**；Mayer open） | Mayer/Bader backlog |
| M5 N 掺杂 𝒮 尺寸趋势不清 | **C-M2** + Table II | `sdc_exp10_synergy_audit.json` (15 pt)；cutoff400 | Results；`tab_S_synergy_grid` | **partial** | `size_6x60_N_pos3pct_cutoff400` |

## Minor Comments

| 要点 | 状态 | 动作 |
|------|------|------|
| m1 花体 𝒮 统一 | **closed** | R251 grep；Fig.1(d) 矢量重导出若需 |
| m2 $E_{\mathrm{sub}}$ 量级说明 | **closed** | `tab_I.tex` 表注强化 |
| m3 B 掺杂 $\lambda^{-}$ 异常 | **partial** | Methods Marcus + Limitations 机制句 |
| m4 图注 N 负 gap | **closed** | Fig.1 caption 金属性说明 |
| m5 引言文献 | **partial** | Intro COF/富勒烯网络句 + bib |
| m6 ≳90 任务界定 | **closed** | `tab_II` caption |

## 写作建议

| 建议 | 状态 | 文稿 |
|------|------|------|
| 摘要背景铺垫 | **closed** | Abstract L40–43 screening 句 |
| 方法长句拆分 | **partial** | `methods_extended.tex` 按需 |
| 设计启示具体化 | **partial** | Discussion Design implications（共价半径 ≳20 pm） |

**Live snapshot（2026-07-05 R393）**：periodic relax **4/4** ✅；population **18/18** ✅；`reference_pbed3` **4/24**（`+2.5_B` **running**，OT~130/300；勿改 Table I）。


## DFT 队列顺序

见 `experiments/run_prb_revision_dft.sh`：

1. Table III relax — **skip if 4/4** ✅
2. seed137 tetramer **24/24** ✅ — skip
3. rigid PBE+D3 Table III matched **4/4** ✅ — skip
4. periodic placement n=4 — **16/16** ✅ — skip
5. **P0** periodic $n{=}1$ P GEO (`periodic_relax_validation/`) — **2/4**；P 角须 `LSD .TRUE.`（`generate_periodic_relax_inputs.py`）
6. population B/N Hirshfeld (`continue_population_bn.sh`) — **0/12**
7. reference placement PBE+D3 α (`reference_pbed3/`) — inputs only
8. Exp10 cutoff400 — idle backlog

**CPU**：`experiments/cp2k_resource.sh`（≤2/3 核）；单路 CP2K。

## 证据闸门

- `alpha_provisional` 任一为 true → **勿**填 `tab_IV` alternate 数值列
- `quantitative_ratio_valid` false → Table III 勿报 matched retention ratio
- 无 `SCF run converged` → 勿进 Results 新定量
