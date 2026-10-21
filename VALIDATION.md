# 验证记录

核验日期：2026-10-20。测试使用独立临时目录，没有安装到任何平台个人技能目录。

## 已完成

- skill-creator 官方 quick_validate.py：通过。
- Python unittest：21项通过，覆盖三表独立算术、现金与留存收益滚动、SBC、净现金桥接、计量单位、情景、反向估值无解/已知根、缺失值、错误费用符号、负资产、RIM/DDM/NAV、行业附表、初始化不覆盖、待完成成果拒绝、51项到22章映射和文件引用。
- 合成制造企业：三种情景的三表和FCFF与独立手算一致；Base每股32.22461484397695仅为合成算例，不是任何真实公司目标价。78项财务检查通过。
- LibreOffice对该合成工作簿的2,461个非缺失公式与Python逐项核对，无数值不一致。未披露/不适用的输入保留有说明的#N/A并传播；不将它们报成已验证的数值。
- 独立行为评审：制造企业、缺资本/资产质量数据的银行、亏损软件企业及无财务披露私企四类。后两类撤回不可支持的估值，不补造客户、融资或财务。银行参数RIM只给条件权益值，行业缺口保持limited，未知股数不报每股值。
- 独立模型评审：三表及FCFF与外部手算、RIM和DDM与封闭解/手算核对；发现的空历史、负股数和负输入问题已修复并回归验证。
- 真实资料抽查：Microsoft官方FY2025 Form10-K的FY2024/2025收入、营业利润、净利润、CFO、现金PP&E支出及资产负债权益。两年CFO减现金CapEx分别74,071与71,611百万USD；两年资产负债勾稽为0。实际引擎重算对照通过。D&A保持未知，未将“depreciation, amortization, and other”误作纯D&A。
- 使用这份真实抽查材料完成受限研究台账的正向验收：status=limited、errors为空；它明确不是一份已完成的公司深度报告。

## 可复现命令

在Skill目录，使用装有openpyxl的Python环境：

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_model.py assets/input.example.json /tmp/company-model-check/model.xlsx
python3 scripts/check_workbook.py /tmp/company-model-check/model.xlsx --recalculate
python3 scripts/build_model.py tests/fixtures/microsoft-fy2025.json /tmp/company-source-check/model.xlsx
python3 scripts/check_workbook.py /tmp/company-source-check/model.xlsx --recalculate
```

Windows选择可写临时目录。若没有LibreOffice，检查会明确记录引擎不可用，不把Python计算冒称Excel引擎验证。

真实抽查来源：[Microsoft FY2025 Annual Report](https://www.microsoft.com/investor/reports/ar25/index.html)，Income Statements p.50、Balance Sheets p.52、Cash Flows p.53；[SEC申报记录](https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/0000950170-25-100235-index.html)，申报日2025-07-30、财年截至2025-06-30。

## 实际边界

本次验证不代表已对全球交易所、全部行业或所有平台版本做端到端实测。Codex/Claude Code通过公开技能规范和相对路径结构核对，未在两个独立产品会话实际调用。

银行/保险资本、资产/准备金、复杂融资和稀释、递延税、租赁、并购及终值再投资应按目标公司补附表；基础估值构件不证明行业完整性。公开资料不足时必须说明限制。

结构校验、来源台账和公式重算不能证明所有事实和自然语言结论正确。最终研究仍要核对原文、正文、期间、单位、行业适配及模型经济合理性。
