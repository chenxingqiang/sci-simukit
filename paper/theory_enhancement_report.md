# 理论增强与证据对齐报告

> **Loop R188 Results + R189 Discussion（2026-06-20）** — (ii) P $|\\mathcal{S}|$ $n{=}4$/max；endohedral vs $\mathcal{S}$ 边界 — Fig.~caption (d) audit 数值落盘 — Methods $|\mathcal{S}|$ 23.7 + post_exp9$\rightarrow$render_si 契约 — Pereira2026 endohedral arXiv:2603.10142 vs substitutional $\mathcal{S}$ — Wang2024simulation 入 Intro；R184 Abstract fifteen-point **落盘** — fifteen-point grid 入 Abstract 对齐 Intro/audit — R183 cover_letter 31.9 — R182 Conclusion (iii) 23.7 — R175--R176 Abstract 31.9 — cover_letter_prl P0 ~32→31.9 — R172--R174 $|\\mathcal{S}|$ 全稿 31.9 对齐；Abstract P0 修复 — R165 Discussion design↔audit；R166 Conclusion+DA 路径 — R155 Methods Exp9；R156 Results/SI 边界；R157 Discussion Marcus；R158 Conclusion defer — R116 PBE/D3；R117 Qiu2025；Conclusion post_exp9 闭环 — 与主稿 / canonical JSON / `.out` 对齐  
> 本文件是**活文档**：旧版「投稿准备 ✅ / 8.5/10」评分已废止；以下以 **A/B/C 证据等级** 为准。

## PRL desk gate（R128+）

| 闸门 | 状态 |
|------|------|
| D6 摘要 ≤600 | **closed** R128 |
| D7 词数 ≤3750 | **closed** R129 (~1787 `texcount`) |
| D2 弛豫 | **open** Table S3 pending |
| D1 叙事锚点 | **partial** R130 Conclusion |

## 证据审计表（主稿可引用边界）

| 主张 | 等级 | 状态 | 来源 |
|------|------|------|------|
| 非加性序参量 $\mathcal{S}$、$H_{eff}$ 框架 | **A** | **[verified]** | `paper/sdc_method_section.tex`, `c/simukit-sdc` |
| Tetramer strain grid $\alpha_{B,N,P}$、Table 1 能量列 | **A** | **[verified]** | `experiments/analysis/table1_verification.json` |
| Size-scaling grid 尺寸标度、40/40 SCF | **A** | **[verified]** | `experiments/analysis/exp10_status.json` |
| Size-scaling grid $\mathcal{S}(n)$ @ +3%（15 点） | **A** | **[verified]** | `experiments/analysis/sdc/sdc_exp10_synergy_audit.json` |
| $\mathcal{S}_\infty$ 外推（B/N/P） | **B** | **[provisional]** | 同上 `size_scaling_fits`；N @ n=8 符号反转需 Discussion 解释 |
| Tetramer PDOS PDOS / gap 叙事链 | **A** | **[verified]** | Exp7 `.out` + `fig_prl_main.py` / `render_prl.sh` |
| Polaron factorial IPR/$J$（2 点） | **A** | **[verified, 2-point]** | `experiments/analysis/exp4_polaron_verification.json` |
| 极化子→带转变 $J>\lambda/2$ | **C** | **[not confirmed]** | Exp4: `polaron_transition_confirmed: false` |
| Charged polaron adiabatic IP/EA | **A−** | **[partial 11/12, SI Fig.~S5]** | `exp9_polaron_verification.json`；主文不引 IP/EA |
| 主稿 Conclusion 四条 ↔ Intro | **A** | **[verified R102]** | 无 transport 倍数 |
| SI Fig.~S5–S6 pipeline | **A** | **[verified]** | `render_si_figures.sh` + `compile_si.sh` / `compile_prb.sh` |
| Methods PBE+D3 citekeys | **A** | **[verified R116]** | `Perdew1996generalized`, `Grimme2011effect` + `cp2k2025` |
| Intro Katiyar2025strain cite | **B+** | **[R162]** | 2D strain review 语境 |
| Intro LopezAlcalay2025 cite | **B+** | **[R169]** | 衍生网络 strain+掺杂 vs $(\epsilon,\delta)$ 交叉项 |
| Intro Makov2023 intrinsic strain | **B+** | **[R170]** | 内禀 cage 应变语境；DOI 10.1038/s41524-023-01167-5 |
| Intro Silva2024 transport | **B+** | **[R177]** | 极化子各向异性语境；Marcus 仍 SI-only |
| Intro Wang2024simulation mechanics | **B+** | **[R185]** | 单轴力学 vs 双轴 $(\epsilon,\delta)$ $\mathcal{S}$ 差异化 |
| Intro 去重复 separate scans | **A** | **[R161]** | joint $(\epsilon,\delta)$ 动机句 |
| SI Overview Exp9 诚实化 | **A−** | **[R161]** | 11/12 + vertical pending |
| Discussion Qiu2025 力学对比 | **B+** | **[verified R154]** | `strain_doped_graphullerene.tex` Context 段 cite `Qiu2025atomic` |
| Abstract partial Exp9 | **N/A** | **[withdrawn R67]** | PRB 摘要无 Exp9 计数 |
| Abstract $\alpha$/|$\mathcal{S}$| vs audit | **A** | **[R175--R176 P0]** | Abstract max $31.9$ 已落盘 `strain_doped_graphullerene.tex` |
| Abstract fifteen-point grid | **A** | **[R184; R185 落盘]** | 与 Intro Eq.~$\\mathcal{S}$ / `sdc_exp10_synergy_audit.json` 一致 |
| Abstract PBE+D3 术语 | **A** | **[R168]** | 与 Methods/Intro `PBE+D3` 一致 |
| Abstract Marcus defer | **A** | **[R160]** | 末句 SI-only；无 $\lambda$ 数值 |
| 主稿 citekey 计数（精简稿） | **A** | **13** | 非 `citation_completion_report` 48 篇旧快照 |
| `running_snapshot` OT 字段 | **A** | **[fixed R103]** | `last_ot_convergence`（非 RMS grad） |
| Marcus $\lambda$（vertical − adiabatic） | **B** | **[pending]** | Exp9: **11/12** GEO_OPT + **0/8** vertical SP；`derived.lambda_eV` 全 null |
| PRL 主图 (a–d) | **A** | **[verified]** | `paper/figures/out/figure_prb_main.pdf` + audit JSON（PRB 修订版；无 inset） |
| PRB 主图 panel (d) $n{=}4$ $\mathcal{S}$ 标注 | **A** | **[verified R135]** | `fig_prl_main.py` `build_prb_figure` |
| Table S5 局域结构（$\bar{d}$, $\Delta r_{\mathrm{cov}}$） | **A−** | **[verified]** | `experiments/analysis/local_structure_tetramer.json` |
| Major 4 论证（$E_{\mathrm{sub}}$, S–$\alpha$, B vs P） | **A** | **[verified R135]** | Discussion + Table S1 |
| PRL transport / Marcus 主图 | **C** | **[pending]** | PRB 主文不阻塞；SI S5–S6 |
| Fig.~S5 P panel | **A−** | **[R150]** | 1$\times$4；P IP 4.07 eV |
| Conclusion 压缩去冗余 | **A** | **[R148]** | 删重复 N/B 句；保留 Tables~S2--S4 |
| Conclusion Marcus/SI defer | **A** | **[R158]** | 与 Discussion R157 边界一致 |
| Results $\mathcal{S}(n)$ audit 溯源 | **A** | **[R164; R172; R188 caption (d) n=4]** | `sdc_exp10_synergy_audit.json` + Fig.~caption (d) |
| Fig.~caption (c) $\alpha$ | Table~S1 | **R180** |
| Discussion design rules ↔ audit | **A** | **[R165; R173; R181 n=4 23.7/6.2]** | HT reranking + verified $n{=}4$ values |
| Discussion Makov2023 baseline | **B+** | **[R173; R178 Context cite]** | 内禀应变 + 刚性外载衔接 |
| Discussion Pereira2026 endohedral | **B+** | **[R186; R189 Polaron 段]** | 笼内 vs 置换正交控制轴 |
| Conclusion + Data availability audit | **A** | **[R166; R174; R182 (iii) 23.7]** | machine-readable reranking + DA 路径 |
| cover_letter_prl $|\\mathcal{S}|$ max | **A** | **[R183 P0]** | 31.9 meV/atom 对齐主稿/audit |
| Results adiabatic IP/EA 边界 | **A** | **[R156]** | 主文不引；11/12 → audit JSON |
| Discussion polaron transport 段 | **A−** | **[R157]** | Capobianco 协议 vs PBE+D3 |
| sdc_method simukit-sdc 点名 | **A** | **[R163; R171; R179 SI hooks]** | `c/simukit-sdc` + `post_exp9/10` + `render_si_figures.sh` |
| Methods Exp9 batch 契约 | **A** | **[R155; R187 render_si]** | `continue_exp9` + `post_exp9` + `render_si_figures.sh` |
| Methods screening $|\\mathcal{S}|$ @ $n{=}4$ P | **A** | **[R187]** | 23.7 meV/atom vs audit（原 $\approx 24$） |
| Exp9 post hook geo 计数 | **A** | **[R152]** | `converged` + `outputs_converged` |
| §8 mapping 废止 Results localization | **A** | **[R147]** | 改 SI Fig.~S5 |
| Conclusion Intro 三问闭环 | **A** | **[verified R146]** | (i)--(iii) 显式回答 |
| Khan2025 vs $\mathcal{S}$ Discussion | **B+** | **[verified R143]** | 深能级 vs 总能量交叉项 |
| SI Table S2 charged polaron 计数 | **A−** | **[verified R141]** | 11/12 GEO_OPT + 0/8 vertical；与 JSON 一致 |
| ML $R^2{>}0.95$、775%/300% $\mu$ | **C** | **[withdrawn from main]** | 勿进 Abstract/Results |
| 下文 IPR 45→25、$J{=}135$ meV、$\mu{=}8.75\times$ | **C** | **[discrepancy]** | 仅作历史理论草稿；见 §2 |

**Track A 快照（2026-06-20，R189）**：Exp9 **11/12** — `polaron_P_qneg1_opt` step **226/300** ~75%（CP2K 不干预）；Exp10 **40/41**；Exp8 **6/6** ✅。

---

## 7b. Methods 截断能契约 (R132)

| 文稿声称 | inp 实际 | 状态 |
|----------|----------|------|
| 400 Ry $n\leq4$, 350 Ry $n\geq6$ | `size_*x60_*.inp` | **A** (R132 修复原 300/280 错误) |
| Table S3 弛豫 | `relax_validation/` + `run_relax_validation.sh` | **B pending** |
| Table S4 seed 137 (18 ENERGY) | `seed_validation/` + `run_seed137_validation.sh` | **B pending** |
| Table S5 局域结构 | `analyze_local_structure.py` | **A− verified** |
| PRB 验证 DFT 队列 | `experiments/run_prb_revision_dft.sh` | **B**（Exp9 空闲后顺序跑） |
| PRB 投稿包 `compile_prb.sh` | 主图 + SI 图 + 双 PDF | **A** **[verified R151]** |

## 8. 主稿段落 ↔ JSON 映射（R103 横切）

| 主稿位置 | 关键量 | JSON / 脚本 |
|----------|--------|-------------|
| Abstract $|\mathcal{S}|$ @ +3% | **A** | **[verified R104]** | audit max 31.9 meV/atom (P, $n=1$)；15 点 |
| SI Fig.~S5 adiabatic IP/EA | pristine/N/B verified；P pending | `exp9_polaron_verification.json` → `derived.adiabatic_eV`（**非主文 Results**） |
| Table 1 | $\alpha$, $E$ | `table1_verification.json` |
| Results §synergy $\mathcal{S}(n)$ | 15 点 `synergy_table` | `sdc_exp10_synergy_audit.json` (**R164--R165**) |
| Fig.~2 caption | 15 点 $\mathcal{S}$ | `sdc_exp10_synergy_audit.json` |
| Limitations | 11/12 GEO, no $\lambda$ | `derived.lambda_eV` 全 null |
| Conclusion (i)–(iii) | Intro 三问显式闭环 | **R146**；Marcus $\lambda$ deferred to SI (**R158** 末句) |
| Conclusion (ii) max $|\mathcal{S}|$ | 31.9 meV/atom | **R174--R175** |
| Conclusion (iii) $n{=}4$ P $|\mathcal{S}|$ | 23.7 meV/atom | **R182** |
| Fig.~main caption (d) | audit JSON | **R172** |
| Data availability synergy audit | `sdc_exp10_synergy_audit.json` | **R166** Conclusion + DA 路径 |
| Discussion design rules | fifteen-point audit HT reranking | `sdc_exp10_synergy_audit.json` (**R165**) |

**grep 闸门（2026-06-20，R183）**：主稿 + `cover_letter_prl.txt` 无 ~32/775%/300%/8.75× ✅；Koopmans/rVV10 仅 Methods/Limitations 对比句 ✅；$|\mathcal{S}|$ max **31.9** meV/atom（主稿 + PRL cover letter）✅

---

## 1. 已验证的理论—计算闭环（可写进主稿）

### 1.1 应变—掺杂非加性（核心贡献）

- **序参量**：$\mathcal{S} = E(\epsilon,\delta) - E(\epsilon,0) - E(0,\delta) + E(0,0)$（meV/atom，Exp5+Exp10）。
- **尺寸标度**：$S(n) \approx S_\infty + A/n$；@+3% strain，15 点 DFT（n=1,2,4,6,8 × B/N/P）；JSON 字段 `synergy_S_meV_per_atom`。
- **Provisional $S_\infty$**（meV/atom）：B **−0.52**，N **−0.68**，P **−0.13**（`sdc_exp10_synergy_audit.json`）。
- **设计含义**：N vs B 应变灵敏度符号相反（Exp5 $\alpha$）；n=8 N 的 $\mathcal{S}$ 符号反转 — 尺寸依赖非加性。

### 1.2 电子结构（Exp7 + 图 3）

- Gap closing、π-PDOS 应变演化、HOMO/LUMO vs $\epsilon$ — 与 Exp7 converged PDOS 一致。

### 1.3 极化子邻域证据（Exp4，两点）

| 体系 | IPR | $J$ (meV) | 判据 |
|------|-----|-----------|------|
| pristine 0% | 75.0 | 26.6 | small polaron hopping |
| B +3% | 45.0 | 37.2 (+40%) | $J < \lambda/2$ → **无** band-like 转变 |

### 1.4 Exp9 charged polaron（11/12 GEO_OPT）

| Dopant | IP (eV) | EA (eV) | 备注 |
|--------|---------|---------|------|
| pristine | 4.73 | 2.61 | GEO converged；**SI Fig.~S5 only**（主文不引） |
| N | 3.89 | 2.77 | GEO converged；**SI Fig.~S5** |
| B | 4.11 | 3.12 | GEO converged；**SI Fig.~S5** |
| P | 4.07 | — | qpos1 converged；qneg1 pending |

Marcus 重组能（待 8× vertical SP）→ `analyze_exp9_polaron.py` → `derived.lambda_eV`；Fig.~S5 由 `fig_si_s5_marcus_pending.py` 读 JSON。

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

## 4. 创新审计（R175）

| 主张 | 等级 |
|------|------|
| graphullerene 非加性 $\mathcal{S}$ + 40/40 | **A** |
| N vs B $\alpha$ 符号相反 | **A** |
| N @ n=8 $\mathcal{S}$ 符号反转 | **B pending** | cutoff400 + Table S4 |
| Exp9 partial IP/EA (SI Fig.~S5) | **A−** | 11/12 GEO\_OPT |
| Discussion HT reranking ↔ audit | **A** | **R165** |
| Conclusion DA synergy path | **A** | **R166** |
| Intro–Conclusion 四条闭环 + Marcus defer | **A** |
| Marcus $\lambda$ | **B pending** |
| 300%/775% mobility | **C** |

---

## 5. 工具入口

```bash
bash experiments/post_exp9_converged.sh   # after each GEO_OPT / vertical SP
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

**检索（R162）**：`graphullerene B N P doping strain DFT 2025` — Khan/Lopez/Qiu 已覆盖；Intro 入 `Katiyar2025strain`（2D strain review，非 $\mathcal{S}$）。
**检索（R157）**：`graphullerene polaron reorganization DFT 2025` — Capobianco2024/Khan2025 已覆盖；无新 bib。
**检索（R137）**：`graphullerene strain doping 2025` — Wang2024 qHP/qTP 各向异性已在 bib；LopezAlcalay2025 graphendofullerene 应变+掺杂（衍生体系）入 Discussion 对比句；endohedral qHP 2026 预印本未入（偏离 B/N 替位主题）。


## 7. SI 图件索引（R94）

| 图 | 路径 | 证据等级 | 备注 |
|----|------|----------|------|
| S4 π-DOS @ ε=0 | `figures/out/figure_s4_pdos_exp7.pdf` | **A−** | Exp7 `.pdos`; MO isosurfaces pending VMD |
| S5 Marcus λ | `figures/out/figure_s5_marcus_pending.pdf` | **B+** | IP/EA from Exp9 JSON; λ pending vertical SP |
| S6 $J$ + FCWD | `figures/out/figure_s6_j_exp4.pdf` | **B+** | (a) Exp4 $J$ **A**; (b) synthetic FCWD pending MolFC |
| S5 局域结构 | Table S5 in `supplementary_figures.tex` | **A−** | `local_structure_tetramer.json` |

渲染：`bash paper/figures/render_si_figures.sh`；PRB 包：`bash paper/compile_prb.sh`
