# 数据和脚本接口

所有命令从 Skill 目录运行；其他目录运行时使用脚本绝对路径。Python 3.10+，生成/读取 Excel 需要 openpyxl。合成输入 `assets/input.example.json` 演示完整格式；复制前把合成数据全部删除，不得修改名称后当真实研究。

```sh
python3 scripts/init_research.py research/company/2026-10-20 --company "Company" --as-of 2026-10-20
python3 scripts/build_model.py research/company/2026-10-20/work/input.json research/company/2026-10-20/model.xlsx
python3 scripts/check_workbook.py research/company/2026-10-20/model.xlsx --recalculate
python3 scripts/validate_research.py research/company/2026-10-20
```

日期是调用示例，执行时替换。初始化拒绝覆盖非空目录。构建器会覆盖指定的模型及同目录 model-results.json，因此更新先保留旧版本或选择新截止日目录。

## input.json

顶层：company、as_of（ISO日期）、currency、money_unit、shares_unit（两者各选units/thousand/million/billion）、industry_type、selected_case（bear/base/bull）、history、scenarios、valuation、provenance、limitations。synthetic仅用于测试；真实研究不得为true。

industry_type 可用 operating/bank/insurance/asset/cyclical/early_growth/private。上市状态另在研究台账记录。股份计量单位独立于货币单位，每股价值自动换算，例如金额million与股数units不可直接相除。

history 按年份升序的记录列表。每条含year与可得财务值；字段见 `scripts/build_model.py` 的 FIELDS。全部流出费用、现金CapEx、债务余额用正数；现金流量 cfo/cfi/cff/fx 保留正负。NWC不含现金/有息债务，只含经营应收、库存、其他经营流动资产减应付/其他经营流动负债。其他资产应包含未单列项目，确保资产分类和披露总额一致。未知为null或省略，不能0填充。

三表 forecast 基线中 opex_pct 是**不含折旧摊销、包含SBC费用**的经营费用率；否则会重复扣除D&A。折旧率针对期初合并PP&E的简化，若摊销重大，应扩展固定/无形资产附表，不把“折旧摊销及其他”整体命名D&A。

scenarios 下 bear/base/bull 各为逐年记录，年数相同。普通企业字段 DRIVERS 全部明确填写（零也须有依据）：

- 比率/增长：growth、cogs_pct、opex_pct、depreciation_rate、capex_pct、ar_pct、inventory_pct、other_ca_pct、ap_pct、other_cl_pct、tax_rate、interest_rate。百分数用小数。
- 金额：debt_issued、debt_repaid、dividends、buybacks、equity_issued、sbc、oci、fx、cfi_other。
- 股数：shares_issued、shares_repur。这里跟踪股数变动，估值分母默认当前已稀释股数；存在未来融资/每股分配变化时，基线会标记受限，需要另建估值分配，不能直接发布静态分母每股价值。

没有有力依据的未来经营驱动可作为明确说明的研究假设；当连起点财务都未知时不得用假设冒充已建完整三表。

valuation.method 选 fcff/rim/ddm/nav/unavailable。

- fcff：wacc、terminal_growth、debt、excess_cash、minority、other_claims、nonoperating_assets、diluted_shares；有可靠市值时填market_cap启用反向估值。reverse_low/high 为统一增长率求解区间，默认-0.5/1.5，是数值求解边界，不是经营预测。折现年末法。
- rim：book_equity、cost_equity、terminal_growth、terminal_roe、terminal_payout、diluted_shares；情景每年含roe和payout。clean-surplus假设须检查OCI/重估等；终值g=ROE×(1−payout)。净融资/回购需在行业扩展中建模。
- ddm：cost_equity、terminal_growth、diluted_shares；情景每年dividend是**总股利金额**，不是每股股利。须另论证资本约束下可分配能力与终值可持续性。
- nav：assets数组，每项name/value（Base）/bear_value/bull_value；价值桥接用debt/excess_cash/minority/other_claims/nonoperating_assets/diluted_shares。资产项若已扣分部债务，集团桥接不能再扣同一笔。未提供Bear/Bull资产价值时对应情景保留未知，不把Base重复显示为三情景。
- unavailable：reason，history保留实际已知值；交付带不可计算说明的Excel，不伪造估值。没有股数可仅报告权益价值，不编每股价格。

provenance 是“JSON字段路径→证据/假设依据”的字典，按最长路径前缀匹配。例如 `history.0.revenue` 或 `scenarios.base.0.growth`；允许同一披露包给history前缀，但重要数字应细化到证据ID与定位。缺来源的数值标 UNTRACED，不能视为已验证。

## 行业附表扩展

银行、保险、资产型和亏损成长企业除估值基本构件外，须补经营/资本/资产或融资约束附表；否则构建器明确列为未完成。`supplemental_schedules` 为数组，每项 name（唯一英文短表名）及 cells（address、value或formula、input_path或note）。公式支持跨表单元格、算术、比较、IF、CHOOSE、MAX、MIN、ABS，不执行任意Python或外部链接。标签用字符串value；数值用input_path关联provenance；null会保留为未知。

`industry_checks` 为数组，每条 name、sheet、address、expected（默认0）、tolerance（默认1e-6）；检查结果不能作为业务预测输入。银行至少核对利润到资本、分红约束、资产质量/资本定义；保险核对可分配利润/准备金或偿付能力；资产型核对资产归属与负债重复；亏损成长核对现金跑道和融资可行性。资料不足时附表留未知并交付limited，不为了通过补造资本要求。

示例：`{"name":"Capital","cells":[{"address":"A1","value":"资本约束"},{"address":"B3","value":100,"input_path":"sector.capital"},{"address":"B4","formula":"='Capital'!B3-100"}]}`；示例常数100必须替换为有来源的真实输入引用，不应写进真实公式。

## 输出与检查

model-results.json 在 model.xlsx **同目录**。包含 formula_values（如Base!B14）、checks、missing、errors、untraced_inputs、输入/工作簿哈希和engine_check。它是Python算术复算，不是Excel缓存。改变输入后重新build再check，不能沿用旧结果。

check_workbook 使用独立临时LibreOffice配置重算副本，将所有预期公式值与Python对照；通过后回写带缓存的工作簿。未知单元格显示有说明的 `#N/A` 并传播，避免空单元格算成零；不把已声明缺失误称为意外公式错误。引擎不存在就记录unavailable，不假称验证。

## 证据、覆盖和数值声明

sources/evidence 字段见 workflow-evidence.md。coverage 每项含id/title/status/report_sections/finding/evidence_ids/reason/impact；status只在完成时改为complete/limited/not_applicable。第49项无文章要求时not_applicable并说明原因；其余流程项记录实际执行结果。

claims 是数组，每项：id、value、unit、period、report_anchor，以及 evidence_id 或 model_ref 二选一。report_anchor 使用正文里的稳定注释，如 `<!-- claim:revenue-2025 -->`，便于人工定位；数值可按展示精度另写，台账保留未四舍五入值。验证器核对台账数值，作者核对正文对应数值及单位，不宣称脚本理解了自然语言。

受限结果仍需解释缺口的判断影响；任何硬性计算错误须修复或明确撤回受影响估值，不能只改状态来掩盖错误。
