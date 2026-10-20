# 安装与使用

此文件夹是完整 Agent Skill，保留 scripts、references、assets、agents 及许可文件的相对位置。需要联网阅读/搜索、读写文件及Python执行能力；没有账号或付费数据库也可研究公开资料。技能不会自行获得网站权限或绕过付费墙。

## Codex

将整个 `comprehensive-company-research` 文件夹复制到个人技能目录 `~/.agents/skills/`，或项目的 `.agents/skills/`。若安装版本/组织有指定目录，以该环境实际配置为准，避免多个同名副本。新建会话后输入：

```text
使用 $comprehensive-company-research 全面研究微软，自动完成报告、Excel和跟踪清单。
```

本机某些既有技能位于旧目录 `~/.codex/skills/`；这不是当前官方文档列出的通用个人目录，迁移时不要误覆盖其他技能。`agents/openai.yaml` 提供Codex界面元数据，不是额外Agent。

依据：[OpenAI官方本地技能位置](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)，2026-10-20核对。

## Claude Code

将整个文件夹复制到 `~/.claude/skills/`，或项目 `.claude/skills/`。在本地Claude Code中调用：

```text
/comprehensive-company-research 全面研究微软，自动完成报告、Excel和跟踪清单。
```

`SKILL.md` 使用两平台通用的 name/description，核心内容不含专属工具名称。Cloud/Cowork不一定读取本机个人目录，按对应环境配置。依据：[Claude Code官方技能文档](https://code.claude.com/docs/en/skills)，2026-10-20核对。

## Python与Excel

Python 3.10+。进入Skill文件夹后，在目标环境的虚拟环境安装依赖，避免修改系统Python：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Windows使用 `.venv\Scripts\python.exe`。运行脚本时使用已安装openpyxl的解释器。Codex若提供捆绑运行时，可由平台工具发现路径，不把本机绝对路径写入技能。

Excel活公式由openpyxl生成；openpyxl不执行公式。实际重算需要可用的LibreOffice（soffice/libreoffice命令），或由目标平台在Excel中重算并用等价方式核对。脚本不会自动安装Office。缺少引擎时Python仍能复算，但交付必须披露未做引擎缓存验证。

## 成果位置与更新

默认 `research/<公司标识>/<截止日>/`，使用 `init_research.py` 创建；脚本不覆盖已有目录。后续财报更新时保留旧版，重新验证受影响证据、预测与反证条件，再重建模型和结论。

安装说明已按官方文件规范核对；不代表已在所有平台版本、权限策略或云端环境做了实际运行测试。
