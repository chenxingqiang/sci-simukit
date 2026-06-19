# 理论增强与证据对齐报告

> **Loop R109 审计（2026-06-18）** — 同步 R106–R108 主图/SI pipeline — 与主稿 / canonical JSON / `.out` 对齐  
> 本文件是**活文档**：旧版「投稿准备 ✅ / 8.5/10」评分已废止；以下以 **A/B/C 证据等级** 为准。

## 证据审计表（主稿可引用边界）

| 主张 | 等级 | 状态 | 来源 |
|------|------|------|------|
| 非加性序参量 $\mathcal{S}$、$H_{eff}$ 框架 | **A** | **[verified]** | `paper/sdc_method_section.tex`, `c/simukit-sdc` |
| Exp.~5 $\alpha_{B,N,P}$、Table 1 能量列 | **A** | **[verified]** | `experiments/analysis/table1_verification.json` |
| Exp.~10 尺寸标度、40/40 SCF | **A** | **[verified]** | `experiments/analysis/exp10_status.json` |
| Exp.~10 $\mathcal{S}(n)$ @ +3%（15 点） | **A** | **[verified]** | `experiments/analysis/sdc/sdc_exp10_synergy_audit.json` |
| $\mathcal{S}_\infty$ 外推（B/N/P） | **B** | **[provisional]** | 同上 `size_scaling_fits`；N @ n=8 符号反转需 Discussion 解释 |
| Exp.~7 PDOS / gap 叙事链 | **A** | **[verified]** | Exp7 `.out` + `fig_prl_main.py` / `render_prl.sh` |
| Exp.~4 IPR/$J$（2 点） | **A** | **[verified, 2-point]** | `experiments/analysis/exp4_polaron_verification.json` |
| 极化子→带转变 $J>\lambda/2$ | **C** | **[not confirmed]** | Exp4: `polaron_transition_confirmed: false` |
| Exp.~9 adiabatic IP/EA | **A−** | **[partial 7/12, in Results]** | `exp9_polaron_verification.json`；Results + Discussion |
| 主稿 Conclusion 四条 ↔ Intro | **A** | **[verified R102]** | 无 transport 倍数 |
| SI Fig S5–S6 + `compile_si.sh` | **B+** | **[S5 schematic; S6 Exp4]** | `render_si_transport.sh` → `figures/out/` |
| Methods Exp9 workflow | **A** | **[verified R99]** | `sec:exp9_workflow` + `*.inp` |
| `running_snapshot` OT 字段 | **A** | **[fixed R103]** | `last_ot_convergence`（非 RMS grad） |
| Marcus $\lambda$（vertical − adiabatic） | **B** | **[pending]** | Exp9: 5 GEO_OPT + 8 vertical SP；`derived.lambda_eV` 全 null |
| PRL 主图 (a–d) | **A** | **[verified]** | `paper/figures/out/figure_prl_main.pdf` + audit JSON |
| PRL transport / Marcus 主图 | **C** | **[pending]** | 阻塞投稿叙事 |
| ML $R^2{>}0.95$、775%/300% $\mu$ | **C** | **[withdrawn from main]** | 勿进 Abstract/Results |
| 下文 IPR 45→25、$J{=}135$ meV、$\mu{=}8.75\times$ | **C** | **[discrepancy]** | 仅作历史理论草稿；见 §2 |

**Track A 快照（2026-06-18，R109）**：Exp9 **7/12** — qneg1 step **63/300** OT~142（ABORT 重启）；Exp10 **40/40** ✅；Exp8 **6/6** ✅。

---

## 8. 主稿段落 ↔ JSON 映射（R103 横切）

| 主稿位置 | 关键量 | JSON / 脚本 |
|----------|--------|-------------|
| Abstract $|\mathcal{S}|$ @ +3% | **A** | **[verified R104]** | audit max 31.9 meV/atom (P, $n=1$)；15 点 |
| Results localization | IP 4.73 / 3.89 eV, EA 3.12 eV | `exp9_polaron_verification.json` → `derived.adiabatic_eV` |
| Table 1 | $\alpha$, $E$ | `table1_verification.json` |
| Fig.~2 caption | 15 点 $\mathcal{S}$ | `sdc_exp10_synergy_audit.json` |
| Limitations | 7/12, no $\lambda$ | `derived.lambda_eV` 全 null |
| Conclusion (1–4) | 四条贡献 | 同 Intro；Exp9 transport deferred |

**grep 闸门（2026-06-18）**：主稿无 775%/300%/8.75×；Koopmans/rVV10 仅 Methods 对比句 ✅

---

## 1. 已验证的理论—计算闭环（可写进主稿）

### 1.1 应变—掺杂非加性（核心贡献）

- **序参量**：$\mathcal{S} = E(\varepsilon,\delta) - E(\varepsilon,0) - E(0,\delta) + E(0,0)$（meV/atom，Exp5+Exp10）。
- **尺寸标度**：$S(n) \approx S_\infty + A/n$；@+3% strain，15 点 DFT（n=1,2,4,6,8 × B/N/P）。
- **Provisional $S_\infty$**（meV/atom）：B **−0.52**，N **−0.68**，P **−0.13**（`sdc_exp10_synergy_audit.json`）。
- **设计含义**：N vs B 应变灵敏度符号相反（Exp5 $\alpha$）；n=8 N 的 $\mathcal{S}$ 符号反转 — 尺寸依赖非加性。

### 1.2 电子结构（Exp7 + 图 3）

- Gap closing、π-PDOS 应变演化、HOMO/LUMO vs $\varepsilon$ — 与 Exp7 converged PDOS 一致。

### 1.3 极化子邻域证据（Exp4，两点）

| 体系 | IPR | $J$ (meV) | 判据 |
|------|-----|-----------|------|
| pristine 0% | 75.0 | 26.6 | small polaron hopping |
| B +3% | 45.0 | 37.2 (+40%) | $J < \lambda/2$ → **无** band-like 转变 |

### 1.4 Exp9 charged polaron（进行中）

| Dopant | IP (eV) | EA (eV) | 备注 |
|--------|---------|---------|------|
| pristine | 4.73 | — | qneg1 pending；**Results 已引 IP** |
| N | 3.89 | — | qneg1 pending；**Results 已引 IP** |
| B | — | 3.12 | qpos1 pending；**Results 已引 EA** |
| P | — | — | qpos1/qneg1 pending |

Marcus 重组能（待 vertical SP）→ `analyze_exp9_polaron.py` → `derived.lambda_eV`。

---

## 2. 历史理论草稿 vs 审计（勿进 Results）

| 旧报告声称 | 审计值 | 处理 |
|------------|--------|------|
| IPR 45→25 | 75→45（Exp4） | discrepancy |
| $J_0{=}75$, $J{=}135$ meV | 27→37 meV | 勿引用 |
| $\mu{=}8.75\times$ | 无独立 $\mu$ 验证 | 主文已降调 |
| 极化子转变已证明 | false | Discussion 定性 only |

SI S1.2 合成 $\lambda$ 分解：**[illustrative, pending Exp9]**；Capobianco2024 ≈0.1 eV 文献锚点。

---

## 3. PRL 差距清单

| 优先级 | 缺口 | 动作 |
|--------|------|------|
| **P0** | Exp9 12/12 + 8 vertical SP | `continue_exp9_pending.sh`（运行中） |
| **P0** | $\lambda$ → Fig.5 | JSON 契约已就绪 |
| **P1** | Transport 主图 | 待 $\lambda$ + $J$ 网格 |

**叙事强度**：NC/PRB 级非加性 **已够**；**PRL** 仍阻塞 transport。

---

## 4. 创新审计（R103）

| 主张 | 等级 |
|------|------|
| graphullerene 非加性 $\mathcal{S}$ + 40/40 | **A** |
| N vs B $\alpha$ 符号相反 | **A** |
| N @ n=8 $\mathcal{S}$ 符号反转 | **A** |
| Exp9 partial IP/EA in Results | **A−** |
| Intro–Conclusion 四条闭环 | **A** |
| Marcus $\lambda$ | **B pending** |
| 300%/775% mobility | **C** |

---

## 5. 工具入口

```bash
bash experiments/exp9_status_line.sh
python3 experiments/analysis/analyze_exp9_polaron.py
./c/simukit-sdc experiments/exp_10_size_scaling/inputs
```

Legacy `analyze_results.py` → 请改用 `analyze_exp9_polaron.py` + `dft_results/exp_9_charged_polaron/outputs/`。

---

## 6. 投稿前检查清单

- [x] Exp10 40/40 + SDC 15 点
- [x] Exp4 两点 IPR/$J$，转变未声称
- [ ] Exp9 12/12 + 8 vertical SP → $\lambda$
- [ ] Transport 主图（PRL）

---

**总结（R109）**：$\mathcal{S}$ 框架与 Exp5/10 **已对齐**；旧「8.5/10 投稿就绪」**废止**。瓶颈：**Exp9 λ + transport**。


## 7. SI 图件索引（R94）

| 图 | 路径 | 证据等级 | 备注 |
|----|------|----------|------|
| S4 VBM/CBM+DOS | `figures/final_figures/` (removed) | **B** | VMD pending |
| S5 Marcus λ | `figures/out/figure_s5_marcus_pending.pdf` | **B+** | IP/EA from Exp9 JSON; λ pending vertical SP |
| S6 $J$ audit | `figures/out/figure_s6_j_exp4.pdf` | **A** | Exp4 JSON; FCWD panel pending |

渲染：`bash paper/figures/render_si_transport.sh`；SI PDF：`bash paper/compile_si.sh`
