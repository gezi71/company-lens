# 来源融合与归属

本技能依据用户提供的《Comprehensive Company Research Agent Prompt》及以下四个项目重新组织、编写。创建/核对日期：2026-10-20。研究清单保留用户提示词51个研究部分与22章成品目录；按用户确认加入全球私企、连续执行、Excel和条件性结论规则。没有复制或执行上游Python脚本。

|来源|采用的方法|本地改写与边界|
|---|---|---|
|[Anthropic financial-services](https://github.com/anthropics/financial-services)|研究/模型/估值/报告分阶段、三表勾稽、comps、DCF、公开资料尽调及单位经济|改为连续执行；去除固定篇幅图表要求、美股固定参数；自行实现计算，不移植其公式代码|
|[tigersking520 stock-analysis-skill](https://github.com/tigersking520/stock-analysis-skill)|质量/增长/价格分开、财务排雷、逆向定价和关键因子跟踪|不沿用统一PE/PS阈值、所有市场强制扣非净利润或个人化仓位策略|
|[tiantizz equity-research-report-skill](https://github.com/tiantizz/equity-research-report-skill)|证据账本、经济特征选估值、模型一致性和可证伪跟踪|采用用户选定的Markdown+Excel+清单；其内部引擎未移植，不能声称本技能复现/验证了上游实现|
|[ByteDance DeerFlow consulting-analysis](https://github.com/bytedance/deer-flow/blob/main/skills/public/consulting-analysis/SKILL.md)|问题/假设/数据需求/分析框架/商业含义|自行补齐采集流程，不套每节词数、每章配图或强制用户心理分析|

具体参考为Anthropic的 initiating-coverage、dcf-model、comps-analysis、3-statement-model、unit-economics、dd-checklist，以及其余三个项目主SKILL及tigersking的逆向/排雷/报告rubric。上游是可变main分支，链接用于定位；未取得可核实commit ID，不以tree SHA冒充固定提交。

上游文件属于参考材料，不构成本技能执行时必须遵守的额外交互限制。移植审查发现的易错口径已在本地重写：WACC使用有息债务与股权市值权重、净现金不产生负债务权重；留存收益滚动不直接加SBC；严格区分D&A与含其他调整的现金流加回项。

## 许可

- Anthropic所选模块适用 [Apache-2.0](https://github.com/anthropics/financial-services/blob/main/LICENSE)。许可正文见 licenses/anthropic-Apache-2.0.txt；本地参考规则为重新编写/修改版本，不代表Anthropic背书。
- tigersking520：MIT，Copyright (c) 2026 川神。
- tiantizz：MIT，Copyright (c) 2026 tiantizz；根目录及Skill目录LICENSE通过GitHub contents API核对。
- DeerFlow：MIT，Copyright (c) 2025 Bytedance Ltd. and/or its affiliates；Copyright (c) 2025-2026 DeerFlow Authors。
- 相应MIT许可保存在 licenses 下。已查四仓库递归树未发现NOTICE文件；不将此结论扩展到无关partner-built资源。

发布者 gezi71 已选择对本项目原创代码、模板和研究规则采用根目录 [MIT License](LICENSE)，Copyright (c) 2026 gezi71。原始提示词的权利归用户；以上上游内容仍保留各自适用许可与归属，根目录MIT不替代上游许可义务。

## 执行效率方法参考

本轮按需读取、完整资料落盘及可定位恢复的方法参考 [muratcankoylan / Agent-Skills-for-Context-Engineering 的 filesystem-context](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/filesystem-context/SKILL.md)，并参考其 [context-optimization](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-optimization/SKILL.md) 中先测量再优化的原则。核验日期2026-10-20；重新编写为本项目台账查询及附录工具，未移植上游脚本或加入运行依赖。

上游MIT，Copyright (c) 2025 Context Engineering Agent Skills Contributors，许可正文保存于 [licenses/context-engineering-MIT.txt](licenses/context-engineering-MIT.txt)。不沿用上游节省比例、允许质量下降的目标或自动多Agent策略；本项目需独立验证质量与实际用量。
