# PRB 中文审稿意见 ↔ 仓库状态映射

> **用途**：对照审稿条目、Loop C ID、证据文件与文稿锚点；**不**替代 `paper/response_to_referees.md` 正文。  
> **更新**：2026-06-25（全力 DFT 计划落地）

## Major Comments

| 中文审稿要点 | Loop C | 证据 / 脚本 | 文稿锚点 | 状态 | 下一 DFT |
|--------------|--------|---------------|----------|------|----------|
| M1 掺杂构型普适性不足；周期无多构型 | **C-M2** (tetramer + periodic) | `seed_validation_tetramer.json`（**0/24** protocol-v2 pending）；`periodic_placement_validation.json`（**16/16** ✅） | Table IV；Results $n{=}4$；Limitations | **partial**（tetramer **open** 0/24 / periodic **A** 16/16） | `placement_validation/` seeds 137+271 |
| M2 离子弛豫（四隅） | **C-M1** | `relax_validation_tetramer.json` (4/4)；`relax_validation_matched_functional.json` (**4/4**, ratio valid) | Table III；`sec:methods_s3_relax` | **closed**（sign **A**；matched rigid **A**） | — |
| M3 四聚体 α vs 周期 𝒮 变量混淆 | **C-M4** | 主稿 grep 无并列数值 | Discussion (v) | **closed** | — |
| M4 机理缺电子结构定量 | **C-M3** | `population_P_n1_strain.json`；Table V | Discussion (iv)–(vi)；Limitations | **open** | `population_validation/` n=1 P ×6 strain + Hirshfeld |
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

**Live snapshot（2026-07-02 R380）**：seed137 **0/24**（outer=3，OT~130/300，OSC）；population **0/6** pending.


## DFT 队列顺序

见 `experiments/run_prb_revision_dft.sh`：

1. Table III relax — **skip if 4/4**
2. seed137 tetramer **0/24** (+ 6 pristine modern) — **blocking**
3. rigid PBE+D3 Table III matched (4 SP)
4. periodic placement n=4 (seeds 137, 271)
5. Exp10 cutoff400
6. n=1 P population (6 SP)

**CPU**：`experiments/cp2k_resource.sh`（≤2/3 核）；单路 CP2K。

## 证据闸门

- `alpha_provisional` 任一为 true → **勿**填 `tab_IV` alternate 数值列
- `quantitative_ratio_valid` false → Table III 勿报 matched retention ratio
- 无 `SCF run converged` → 勿进 Results 新定量
