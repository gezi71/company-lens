# 执行与证据规范

## 阶段与恢复

阶段为 identity → plan → evidence → analysis → model → adversarial → report → validation。`state.json` 每阶段记录 pending/in_progress/complete/limited、产物、缺口及下一步。恢复时先核对身份/截止日/财报版本，复用有效台账；新披露或截止日改变时重算受影响部分。不要把旧观点静默当作新结论。

默认成果为 report.md、model.xlsx、tracker.md；work 下保存 input.json、sources.json、evidence.json、coverage.json、claims.json 和 model-results.json。原始下载文件放 work/raw，遵守网站许可与访问权限。研究清单和台账是必要工作底稿，不另输出重复总结。

## 来源获取

1. 先官网 IR、交易所及监管文件，确认法律实体、报告期间、合并范围、重述和准则。母公司、子公司、ADR、双重上市不可混淆。
2. 全球按所在地发现官方入口：美国 SEC；内地巨潮/交易所；香港 HKEX；英国 Companies House/FCA；日本 EDINET/JPX；韩国 DART；新加坡 SGX；澳大利亚 ASX；欧洲当地监管机构和公司法定报告。它们是入口提示，实际 URL 通过搜索确认。
3. 原文读取年报、最新中报/季报、公告、投资者日、电话会及债务附注。新闻摘要只能帮助定位，不能代替原文。
4. 财务覆盖五年，必要时十年/完整周期；若存续或披露不足，列实际可得年数。区分财年/自然年、流量/时点、TTM/全年、总额/净额、报告/调整口径。
5. 对行业和商业说法，找协会、统计、客户/供应商披露、技术资料及监管数据；公司引述的同一咨询调查不是第二个独立来源。
6. 媒体、独立研究、社群与另类数据用于发现遗漏和验证。评论样本、招聘数、流量估计有选择偏差，不能当市场全体或收入事实。

## 证据台账

sources 每条：id、title、url或local_path、publisher、published_at、accessed_at、locator、origin_id、tier。发布日期不可由抓取日期代替；网页无日期时标 unknown。origin_id 标识原始证据，同源转载共用它。非公开文件只保存用户授权范围。

evidence 每条：id、kind、claim、source_ids、period、currency、unit、value、locator、confidence、limitations。kind 是 fact/management_claim/market_estimate/assumption/inference；数字如不适用不强填币种。推断和计算追加 basis_ids 与 formula。保留原始单位，转换单列公式和汇率日期。

重要结论尽力两类独立证据验证；法定报表原值以官方为锚，不强求两份同等权威原件。不足时标证据单一及判断影响。遇冲突列双方定义、时间及可能原因，不能简单平均。

## 截止日与市场预期

默认当前资料截止日；历史截止日研究只能使用当时已公开的信息。价格、股本、FX、债务、共识预测标各自时间戳，说明错配和桥接。股价总回报须处理拆股与分红，不能用事后涨跌证明当时必然正确。

区分管理层指引、分析师共识、媒体叙事和反向估值。无法获得共识时不得把自己的预测叫市场一致预期。非上市公司可研究融资条款、同业和公开交易；普通股、优先股、控制权和清算优先权不同，不直接把融资估值作为普通股价值。

## 停止与缺口

完整覆盖意味着每项有发现或明确限制，并非所有数据都能找到。记录尝试过的官方/独立入口；同一访问问题尝试一次合理替代后继续其他研究，不循环撞付费墙。边际搜索已不能改变重要假设且覆盖有交代时进入交付。关键财务缺失可交付定性结果和待补资料，不制造完整估值。

缺少网络：仅研究用户资料，标受限，不能称已验证最新信息。缺少 Python/openpyxl：完成资料与报告，明确 Excel 未完成并给补救路径，不把 CSV 改扩展名冒充模型。缺少重算引擎：可交付活公式，但声明缓存未核验，Python复算不等于Excel引擎实测。
