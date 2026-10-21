# Company Lens

[简体中文](README.md) | [English](README.en.md)

**Company Lens** 是面向 Codex 与 Claude Code 的公司深度研究 Skill。基于公开一手资料，研究全球上市及非上市公司的商业模式、行业竞争、财务质量、风险和估值，交付 **22 章中文报告、可复算 Excel 模型和研究跟踪清单**。

研究始终分别判断：**公司质量如何、增长能否兑现、价格是否合理**，并说明什么证据会推翻当前结论。

[快速开始](#快速开始) · [使用示例](#使用示例) · [数据来源](#数据来源) · [交付成果](#交付成果) · [模型能力](#模型能力) · [验证与边界](#验证与边界) · [下载试用版](https://github.com/gezi71/company-lens/releases/tag/v0.1.0)

> 当前为 `v0.1.0` 试用版。研究需要 Agent 具备搜索、原文阅读、文件读写和 Python 执行能力。支持范围与实际测试范围见下文。

## 适用场景

- **首次研究一家公司**：理解公司卖什么、卖给谁、如何赚钱，以及竞争者为什么难以复制。
- **基本面与估值研究**：检查利润、现金、资本需求和稀释，分析观察价格隐含的经营预期。
- **新财报后的研究更新**：结合已保存的工作底稿，重新核验受到影响的事实、假设和反证条件。
- **非上市公司公开资料研究**：整理可验证的业务、行业、治理及风险信息，列清需要进一步取得的资料。
- **研究写作**：先完成研究与证据整理；明确要求文章模式时，再生成 Substack 风格文章。

全球覆盖通过查找公司所在地的监管披露与当地语言资料实现；可取得的数据、研究深度及估值能力取决于具体公司的披露情况。

## 快速开始

### 1. 安装到你使用的平台

以下为 macOS / Linux 的个人安装示例，选择对应平台运行。目标目录已存在时，先检查已有副本，避免重复安装。

仓库名为 `company-lens`，安装目录与技能调用名保留为 `comprehensive-company-research`，兼容已有安装。

**Codex**

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gezi71/company-lens.git \
  ~/.agents/skills/comprehensive-company-research
```

**Claude Code**

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/gezi71/company-lens.git \
  ~/.claude/skills/comprehensive-company-research
```

也可以下载 [Release ZIP](https://github.com/gezi71/company-lens/releases/tag/v0.1.0)，解压后将整个 `comprehensive-company-research` 文件夹放入对应技能目录，保留内部文件结构。

最新效率工具请使用上面的 Git 安装方式更新 `main`；`v0.1.0` ZIP 保留为原始试用版，不包含后续改动。

项目级安装、Windows 路径和完整配置见 [INSTALL.md](INSTALL.md)。安装位置依据 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) 与 [Claude Code 官方技能文档](https://code.claude.com/docs/en/skills)核对；组织策略或云端环境可能使用不同的加载方式。

### 2. 准备模型运行环境

在所安装的 Skill 文件夹中，使用 Python **3.10 或更高版本**建立虚拟环境：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

生成 Excel 需要 `openpyxl`。让 Agent 使用已安装依赖的 Python 解释器；若平台自带可用环境，也可以直接使用。Windows 请参照 [安装说明](INSTALL.md)。

实际 Excel 兼容引擎重算需要可用的 LibreOffice（`soffice` 或 `libreoffice`），或在目标环境中进行等价核对。没有引擎时仍可进行 Python 算术复算，但交付会明确说明尚未验证公式缓存。

### 3. 发起研究

Codex：

```text
使用 $comprehensive-company-research 全面研究微软，自动完成中文报告、Excel 模型和跟踪清单。
```

Claude Code：

```text
/comprehensive-company-research 全面研究微软，自动完成中文报告、Excel 模型和跟踪清单。
```

默认使用当前资料截止日；名称或上市实体存在歧义时先确认，其余阶段自动推进。若技能未被发现，检查安装路径、文件夹结构和当前会话的技能列表，必要时重启会话。

## 使用示例

安装后，可在对应平台的技能调用后补充以下要求。

| 场景 | 示例研究要求 |
|---|---|
| 全球上市公司 | 全面研究腾讯控股，重点核验游戏、广告和金融科技业务的收入质量、资本配置及估值隐含预期，其他适用维度也要覆盖。 |
| 结合已有文件 | 全面研究这家公司，结合我提供的年报和 Excel，核验重要数据来源，并明确资料截止日。 |
| 非上市公司 | 研究一家工业传感器私企；公开财务不足时，完成可核实的业务、竞争与风险分析，给出待补资料清单。 |
| 历史截止日 | 只使用截至 2025-12-31 已公开的信息研究这家公司，不使用之后发布的财报和事件。 |
| 财报更新 | 基于已有研究目录，结合最新财报更新关键事实、模型假设、估值与 Thesis Killers，保留旧版。 |
| 文章模式 | 完成全面研究后，再围绕一个核心问题输出 Substack 风格文章，保留关键来源和反方观点。 |

## 研究范围

| 方向 | 核心内容 |
|---|---|
| 公司与商业模式 | 实际业务、收入结构、量价、地区与渠道、有机增长、并购和汇率影响 |
| 产品、技术与研发 | 产品竞争力、定价、用户评价、技术路线、研发投入及成果 |
| 行业与竞争 | TAM / SAM / SOM、产业链、行业结构、周期、同行、替代技术及护城河证据 |
| 客户与供应链 | 客户集中度、留存、切换成本、单位经济、关键供应商及供应瓶颈 |
| 财务与资本 | 历史三表、利润与现金、营运资本、资本开支、债务、会计调整、回购及稀释 |
| 管理层与组织 | 承诺兑现、治理激励、员工与招聘、持股及资本配置结果 |
| 风险与反方 | 最强空头观点、诉讼、监管、宏观、地缘政治及可观察的证伪条件 |
| 估值与预期 | 当前和历史估值、同业比较、适用内在估值、反向估值、三情景及催化 |

原始研究框架的 **51 个部分**逐项映射到成品报告。流程要求、写作规范与可选文章模式也有处理记录；覆盖清单会注明发现、对应章节、证据或限制，不能只标记“已研究”。详见 [研究清单](references/research-map.md)。

## 数据来源

数据由运行研究的 Agent 联网取得，也可以结合用户提供的文件。默认公开免费资料，有权限的专业数据源可作补充。

| 数据 | 主要来源与处理方式 |
|---|---|
| 财务与经营 | 年报、季报、招股书、财报公告、财务附注；重要数字回到原始文件核验 |
| 管理层与战略 | 公司官网、投资者关系页面、电话会、投资者日及重大公告 |
| 法定与监管披露 | SEC、内地交易所与巨潮、HKEX，以及公司所在地的监管机构和法定报告入口 |
| 行业与竞争 | 政府统计、行业协会、竞争者以及客户、供应商的公开披露 |
| 行情与估值 | 可访问的公开价格、市值、股本、同业及历史估值数据，标明时间戳和口径 |
| 辅助证据 | 可靠媒体、独立研究、空头报告、产品评价、招聘、专利与社区讨论 |
| 用户提供资料 | 年报、Excel、行业报告及公司文件，注明来源与独立核验情况 |

重要数据保留期间、币种、单位和原文定位。事实、管理层说法、市场预测、研究假设及推断分别标记；转载同一份资料不算独立验证。

未披露、访问受限或无法取得的数据保持未知。私企缺少核心财务时会限制估值结论；社区讨论与另类数据用于发现问题和辅助验证。Skill 不要求金融数据库 API Key，Agent 本身的账号、联网权限和运行环境由所用平台提供。

## 交付成果

| 成果 | 内容与用途 |
|---|---|
| **`report.md`** | 22 章中文研究报告，附51项覆盖表、来源、争议、资料缺口及模型检查说明 |
| **`model.xlsx`** | 历史财务、经营假设、预测、适用估值、情景与敏感性；保留可修改公式及输入来源 |
| **`tracker.md`** | 指标基准、验证条件、来源、更新频率、受影响假设及需要重评的结论 |

默认研究目录示意：

```text
research/<公司标识>/<资料截止日>/
├── report.md
├── model.xlsx
├── model-results.json       # 算术复算与引擎检查结果
├── tracker.md
├── state.json               # 阶段状态、缺口及下一步
└── work/
    ├── input.json           # 可复算的模型输入
    ├── sources.json         # 来源台账
    ├── evidence.json        # 证据、假设与推断
    ├── coverage.json        # 51项研究覆盖记录
    ├── claims.json          # 重要数值与证据/模型的对应关系
    └── raw/                 # 按访问许可保留的原始资料
```

只有明确要求文章模式时，额外交付 `article.md`。工作底稿用于追溯和更新；资料不足的成果会说明限制及其对判断的影响。

<details>
<summary>查看完整 22 章报告目录</summary>

1. Executive Summary
2. The One-Sentence Thesis
3. Why Now?
4. What Does the Company Actually Do?
5. How It Makes Money
6. Revenue Breakdown
7. Financial History
8. Unit Economics
9. Industry
10. Competitive Landscape
11. Moat
12. Management
13. Capital Allocation
14. Growth Drivers
15. What the Market Is Missing
16. Bear Case
17. Risks
18. Valuation
19. Bull / Base / Bear
20. Catalysts
21. Thesis Killers
22. Final Verdict

标题顺序固定，正文默认中文。不适用的章节保留并解释原因。参见 [报告模板](assets/report-template.md) 与 [报告标准](references/report-contract.md)。

</details>

## 模型能力

| 企业类型 | 方法与约束 |
|---|---|
| 普通经营企业 | 数据充分时原则上五年历史、五年预测，建立三表联动、企业自由现金流（FCFF）与加权资本成本（WACC）估值；有可靠价格时分析隐含预期 |
| 银行与保险 | 使用权益成本下的剩余收益或股利模型，并补充资本、资产质量、准备金或偿付能力分析 |
| 资产与控股企业 | 净资产价值（NAV）或披露支持的分部估值，检查资产归属及负债重复计算 |
| 周期企业 | 参考完整周期与中周期假设，检验峰值利润和资本开支的可持续性 |
| 亏损成长企业 | 分析单位经济、现金跑道、亏损收敛、融资和稀释情景 |
| 非上市公司 | 按对应行业研究；核心财务、交易价格或股权条款未知时限制估值及市场预期分析 |

脚本提供普通企业三表 / FCFF、剩余收益、股利与 NAV 的基础构件。悲观、基准和乐观情景分别计算；缺少情景数据时保持未知。行业专属资本、准备金、复杂税项、租赁、并购和融资附表仍须 Agent 按实际披露补充。

重要口径包括现金流与折现率匹配、企业价值到股权价值桥接、计量单位、SBC 与稀释，以及反向估值的固定参数和求解变量。方法说明见 [modeling.md](references/modeling.md)，输入字段与脚本接口见 [data-contract.md](references/data-contract.md)。

## 执行与质量检查

```mermaid
flowchart LR
    A[确认公司与截止日] --> B[研究问题与覆盖计划]
    B --> C[采集原文与核验证据]
    C --> D[商业分析与财务建模]
    D --> E[估值与反方检验]
    E --> F[报告与跟踪清单]
    F --> G[检查并交付]
```

- **来源检查**：对齐实体、期间、币种、准则和合并范围，保留重要原文定位与冲突说明。
- **计算检查**：核对三表、现金与权益滚动、估值桥接、情景及敏感性。Python 复算与实际引擎重算的状态分别记录。
- **一致性检查**：重要数值关联模型或证据，检查台账引用、研究覆盖及成品结构；作者还须核对正文和原文。
- **反方检验**：认真处理最强反对意见，列出可观察的证伪条件；允许没有可证实的市场预期差。
- **评分依据**：保留七项十分制评分，附证据与方向；资料不足允许不评分，风险高分代表高风险。

阶段材料随研究保存，方便中断后继续。资料不足时可交付条件性结论，受影响部分保持 `limited`，不称为全面核实。

## 复用工具与 token 实测

完整研究仍覆盖51项、22章、Excel模型、反方检验和最终验收。优化集中在复用原文与证据、按章节读取细则，以及用脚本生成固定附录；不通过缩短报告或减少核验节省用量。

- **按需读取**：51项导航保留全貌，581条细则集中在JSON；按章查询会保留相关来源、限制、冲突和递归推断依据。
- **复用底稿**：恢复前核对主体、截止日和披露版本，再复用有效资料；有新披露或重述时重核受影响内容。
- **固定内容自动生成**：附录A由覆盖台账生成，保持完整51行；模型检查可只在控制台返回计数和样例，完整明细保留本地。

```sh
python3 scripts/research_context.py status <研究目录>
python3 scripts/research_context.py section <研究目录> 7
python3 scripts/research_context.py model <研究目录> 'Base!B5' 'Valuation!B23'
python3 scripts/research_context.py coverage <研究目录>
```

模型构建和工作簿检查支持可选 `--summary`，不改变计算、检查或退出规则。查询工具只读已有台账，不证明其仍然有效，也不替代全局验收。新增工具仅用Python标准库，没有新运行依赖。详见[数据接口](references/data-contract.md)。

微软完整对照中，计入质量补充后，总token增加12.70%，未验证整轮节省。因此状态/章节查询保留为可选工具，不作为默认必经步骤。清单、22章报告、Excel与核验要求保持；不承诺节省比例。完整计量、缓存影响及测试边界见[验证记录](VALIDATION.md)。

## 验证与边界

已记录的验证包括：

- **21 项自动测试**，覆盖财务算术、情景、缺失值与错误输入、行业模型基础构件、文件引用和报告映射。
- **四类公司独立行为评审**：制造企业、资料不全的银行、亏损软件企业、无财务披露私企。
- **LibreOffice 公式核对**：合成制造企业模型的 2,461 个非缺失公式与 Python 结果逐项一致。
- **真实资料抽查**：核对 Microsoft FY2025 财报中的两年公开财务原值、历史现金流观察指标与资产负债勾稽。

完整记录和可复现命令见 [VALIDATION.md](VALIDATION.md)。两平台已按技能文件规范及相对路径结构核对，尚未在两个独立产品会话完成实际调用验证；真实资料抽查也不等于已跑完真实公司的完整22章研究报告。

研究依赖可取得的资料、Agent 的阅读判断和模型假设。结构与计算检查不能证明所有事实和叙述正确；使用结论前应核对重要原文、口径及模型的经济合理性。

## 常见问题

**只输入公司名称就可以吗？**

可以。Agent 会先确认主体并建立研究计划。名称存在歧义时需要补充信息；也可以主动提供代码、交易所、截止日及已有资料。

**没有付费金融数据库也能用吗？**

可以从公开披露开展研究。无法访问的共识预测、客户数据或行业统计会注明缺口，不以估计数冒充事实。

**能保证每家公司都有完整五年历史和估值吗？**

研究按实际存续年限和披露取得资料。关键起点财务不足时，不强算完整模型；无可靠价格时，市场隐含预期可能不适用。

**跟踪清单会自动定时更新吗？**

清单记录后续核验方法和频率。更新时需再次发起研究请求；仓库本身没有定时任务。

**怎样更新已安装的 Skill？**

在通过 Git 安装的技能目录执行 `git pull --ff-only`。有本地改动时先检查差异，再决定合并方式。ZIP 安装可下载新版本并保留自己的修改。

已有 Git 安装可将远程地址更新为新仓库：

```bash
git remote set-url origin https://github.com/gezi71/company-lens.git
```

## 项目文件

| 位置 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | Agent 的主入口、执行顺序和关键规则 |
| [references/](references/) | 研究清单、证据规范、行业方法、报告要求与接口 |
| [assets/](assets/) | 报告与跟踪模板、研究映射及明确标注的合成输入 |
| [scripts/](scripts/) | 工作目录初始化、建模、公式重算核对及研究验收 |
| [tests/](tests/) | 自动测试和公开财报抽查输入 |
| [agents/openai.yaml](agents/openai.yaml) | Codex 的技能界面元数据 |

`assets/input.example.json` 是合成算例，不能改名后作为真实公司数据；测试中的财报输入也只覆盖明确声明的抽查范围。

## 来源与许可

本项目依据完整公司研究提示词，并参考以下项目的方法重新组织、编写：

| 来源 | 融合的方法 |
|---|---|
| [Anthropic financial-services](https://github.com/anthropics/financial-services) | 分阶段研究、财务建模、同业比较、单位经济与尽调检查 |
| [tigersking520 stock-analysis-skill](https://github.com/tigersking520/stock-analysis-skill) | 质量、增长与价格分开判断，财务排雷、逆向定价及反证跟踪 |
| [tiantizz equity-research-report-skill](https://github.com/tiantizz/equity-research-report-skill) | 证据台账、行业方法选择、模型一致性与可验证交付 |
| [ByteDance DeerFlow consulting-analysis](https://github.com/bytedance/deer-flow/blob/main/skills/public/consulting-analysis/SKILL.md) | 核心问题、假设、数据需求、分析框架与商业含义 |

没有复制上游 Python 引擎，也不代表上游作者背书。具体归属、改写边界和适用上游许可见 [SOURCES.md](SOURCES.md) 及 [licenses/](licenses/)。

原创部分采用 [MIT License](LICENSE)，Copyright (c) 2026 gezi71。

仅供研究参考，不构成个人化交易建议。
