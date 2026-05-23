# FreshBench: AI Benchmark 保鲜子网

整理时间：2026-05-23

相关文档：

- [技术栈搭建建议](technical-stack.md)
- [Bittensor 官方资源与调研入口](official-resources.md)
- [黑客松往届获奖 Idea 参考](hackathon-idea-references.md)

## 1. One-liner

FreshBench 是一个面向 AI 评测的 Bittensor 子网：矿工持续生产全新的、带可验证答案的评测任务，验证者通过答案校验、新颖性检测、模型组校准和公开挑战机制，筛选出真正能区分模型能力的高质量 benchmark assets。

一句话版：

> FreshBench does not reward question volume. It rewards benchmark assets that survive verification, model-panel calibration, public challenge, and real-world usage.

中文表达：

> FreshBench 不奖励出题数量，只奖励那些经过答案验证、模型组校准、公开挑战和真实使用后仍然有效的评测资产。

## 2. Problem

AI 模型评测正在失真。

过去几年，MMLU、HumanEval、GSM8K、SWE-bench 等主流 benchmark 已经成为模型训练、调参和宣传材料的一部分。越来越多模型在公开榜单上分数很高，但真实使用时仍然会出现推理失败、代码修复失败、工具调用错误、文档理解不稳等问题。

核心问题不是缺少 benchmark，而是缺少持续生产 fresh benchmark 的机制：

- 公开 benchmark 容易被训练数据污染。
- 中心化评测机构更新速度慢，覆盖视角有限。
- 企业和研究者需要更贴近真实任务的新鲜评测集。
- 现有评测题一旦公开太久，就会从“能力测试”退化成“记忆测试”。
- 简单堆更多题不能解决问题，反而可能产生大量低质量 AI 生成题。

因此，AI 评测需要从静态题库变成动态市场：持续生成、验证、挑战、淘汰和更新。

## 3. Subnet Commodity

FreshBench 的核心商品不是“题目数量”，而是可验证、可购买、可复用的 benchmark assets。

一个 benchmark asset 至少包含：

- 评测任务本体：题目、输入、上下文、文件、代码环境或文档。
- 标准答案或可执行验证方式。
- 解题过程或验证证明。
- 能力标签，例如 reasoning、coding、math、document extraction、tool-use、RAG fidelity。
- 难度估计。
- 新颖性证据。
- 适用的评分脚本或 rubric。

示例商品：

- 一道带隐藏测试的代码修复题。
- 一组带字段级 ground truth 的文档结构化提取样本。
- 一个可在沙箱中验证的 agent tool-use 任务。
- 一道有唯一答案、可由 symbolic solver 验证的数学推理题。
- 一个带引用 span 的 RAG 忠实度测试任务。

## 4. Why Bittensor

FreshBench 适合 Bittensor，因为 benchmark 保鲜天然是一个开放、竞争、持续迭代的问题。

中心化团队很难长期覆盖所有能力、语言、地区、行业和新模型失败模式。Bittensor 可以把这个问题变成开放市场：

- 全球矿工从不同领域、语言和任务场景中生成新评测资产。
- 验证者用统一规则筛选、校准、打分。
- 题目不是一次性发布，而是在网络中持续被挑战、使用和淘汰。
- 奖励机制推动矿工生产更有区分度、更难污染、更贴近真实任务的评测资产。

这不是普通 Web3 应用，也不是简单 AI 出题工具。FreshBench 是一个用去中心化激励机制维护 AI 评测新鲜度的基础设施。

## 5. Roles

### Miner: Benchmark Asset Producer

矿工负责提交新的 benchmark assets。

矿工提交内容包括：

```json
{
  "task_id": "freshbench_xxx",
  "task_type": "coding | math | document_extraction | rag | tool_use",
  "task": "...",
  "answer": "...",
  "solution_trace": "...",
  "skill_tags": ["multi_step_reasoning", "schema_following"],
  "difficulty_estimate": 0.62,
  "verification_method": "unit_test | exact_match | symbolic_solver | citation_span | sandbox_execution",
  "scoring_script": "...",
  "source_type": "synthetic | transformed_real_task | human_authored",
  "anti_contamination_evidence": "...",
  "failure_modes_tested": ["shortcut_reasoning", "memorized_pattern", "format_distraction"]
}
```

矿工可以使用人类专家、LLM、程序生成器、真实业务数据变体、公开数据重构等方式生成任务，但必须提交可验证答案和质量证据。

### Validator: Quality Gatekeeper

验证者负责判断矿工提交的评测资产是否值得进入评测池，并为其分配奖励权重。

验证者主要执行：

- Schema 检查：提交格式是否完整。
- 答案有效性检查：答案是否正确、是否唯一、是否可复现。
- 新颖性检查：是否和公开 benchmark、网页内容、历史提交高度相似。
- 难度校准：是否太简单、太难、或无意义。
- 模型组测试：用多类模型和 solver 观察题目的区分能力。
- 反作弊检测：检测重复提交、低成本变体、题目泄露、错误 ground truth。
- 挑战处理：处理其他参与者对题目的反证。

### User / Buyer

潜在用户包括：

- AI 实验室：需要新鲜评测集检测真实能力。
- 模型评测平台：需要动态 benchmark 扩展题池。
- 企业采购方：需要独立评估不同模型在真实业务任务中的表现。
- 研究机构：需要可追踪、可验证、可复现的评测资产。
- Bittensor 生态子网：需要评估 agent、模型、推理服务或数据能力。

## 6. Validation Pipeline

FreshBench 不允许题目提交后直接进入奖励池。每个资产要经过多级过滤。

### Stage 1: Schema and Format Check

验证提交是否包含必要字段：

- task
- answer 或 verification method
- skill tags
- difficulty estimate
- scoring method
- source type
- anti-contamination evidence

缺少核心字段的提交直接拒绝。

### Stage 2: Ground Truth Validity

根据题型采用不同验证方式：

- 数学题：symbolic solver、数值校验、独立解法交叉验证。
- 代码题：单元测试、隐藏测试、mutation testing。
- 文档提取题：字段级 exact match、F1、schema compliance。
- RAG 题：答案必须能映射到原文引用 span。
- Tool-use 题：在沙箱环境中执行并验证最终状态。

如果 ground truth 错误、多解未说明、题目歧义严重，则 validity score 为 0。

### Stage 3: Novelty and Contamination Check

验证者检查题目是否已经存在或过度接近已有材料：

- 与公开 benchmark 做文本相似度和语义相似度检索。
- 与历史提交做去重。
- 搜索公开网页和代码仓库中的近似内容。
- 检测是否只是老题改数字、换变量名、改措辞。

高度相似的题目会被拒绝或大幅降权。

### Stage 4: Model Panel Calibration

验证者维护一个 model panel，用不同能力层级的模型测试题目。

模型组可以包括：

- 小模型 baseline。
- 中等开源模型。
- 强闭源模型。
- 专项 solver 或规则 baseline。
- 人类或专家抽检样本。

题目质量不只看题目本身，而看它在模型组上的表现曲线。

理想题目应该具备：

- 弱模型失败。
- 中等模型部分成功。
- 强模型也不总是稳定成功。
- 错误模式和题目能力标签相关。
- 解题路径不是简单记忆或 shortcut。

不理想题目包括：

- 所有模型都秒答：太简单或疑似污染。
- 所有模型随机失败：太难、歧义或质量差。
- 多个强模型输出几乎一字不差：疑似已泄露或已被训练。
- 模型失败原因和目标能力无关：题目噪音。

### Stage 5: Public Challenge

进入 active pool 的题目可以被其他矿工或验证者挑战。

可挑战原因：

- 答案错误。
- 存在多个合理答案。
- 题目来自已有 benchmark 或公开网页。
- 题目可以被 trivial shortcut 解出。
- 能力标签错误。
- 题目表述依赖奇怪陷阱，不测真实能力。
- scoring script 有漏洞。

挑战成功后：

- 原题降权、移除或退休。
- 原提交者失去部分未释放奖励。
- 挑战者获得奖励。
- 矿工信誉下降。

## 7. Scoring Formula

FreshBench 的评分目标是奖励“长期有效的评测资产”，而不是奖励题目数量。

基础评分：

```text
asset_score =
  validity_score
  * novelty_score
  * discrimination_score
  * reproducibility_score
  * skill_relevance_score
  * usage_score
  * challenge_survival_score
```

各项说明：

- validity_score：答案是否正确、唯一、可验证。
- novelty_score：是否足够新鲜，是否远离已知 benchmark 和历史提交。
- discrimination_score：是否能区分不同能力模型。
- reproducibility_score：不同验证者是否能得到一致评分。
- skill_relevance_score：题目是否真的测试标注能力。
- usage_score：后续真实评测中是否被采用、是否持续有区分度。
- challenge_survival_score：是否经受公开挑战。

任一严重失败项可以触发归零：

```text
if validity_score == 0:
  asset_score = 0

if plagiarism_detected:
  asset_score = 0

if malicious_submission_detected:
  asset_score = 0
```

## 8. Reward Mechanism

奖励分为两段，避免矿工靠刷量套利。

### Submission Reward

题目通过基础验证后，矿工获得少量即时奖励。

目的：

- 鼓励持续提交。
- 覆盖矿工生成和标注成本。
- 但避免垃圾题靠数量拿走主要奖励。

### Usage Reward

题目进入 active pool 后，根据真实使用表现持续释放主要奖励。

释放依据：

- 是否被评测任务采样。
- 是否保持合理区分度。
- 是否被挑战成功。
- 是否在不同模型迭代中仍然有效。
- 是否被外部客户购买或引用。

这种设计让矿工追求长期质量，而不是短期刷题。

## 9. Anti-Gaming

### Attack 1: AI 批量生成垃圾题刷量

防御：

- 不按提交数量奖励。
- 低质量题无法通过 validity、discrimination 和 challenge survival。
- 矿工信誉和通过率挂钩。
- 高频低质提交触发冷却或押金提高。

### Attack 2: 抄袭公开 benchmark 或网页题

防御：

- 公开 benchmark 相似度检索。
- 历史提交去重。
- 语义相似度和结构相似度检测。
- 挑战者可提交来源证据并获得奖励。

### Attack 3: 提交答案错误或多解题

防御：

- 多 solver 交叉验证。
- 可执行验证脚本。
- 被挑战成功后扣除未释放奖励。
- validity score 为 0 时整题归零。

### Attack 4: 生成怪题，让所有模型都失败

防御：

- model panel calibration。
- 人类或专家抽检高价值样本。
- discrimination score 要求合理能力梯度。
- skill relevance score 惩罚无意义陷阱题。

### Attack 5: 生成太简单的题或换皮题

防御：

- 所有模型秒答会降低 discrimination score。
- 只改变量、数字、措辞会被 novelty check 降权。
- benchmark pool 有 active / saturated / retired 生命周期。

### Attack 6: Validator 和 Miner 串通

防御：

- 多验证者交叉评分。
- 评分脚本和结果公开可复现。
- 异常评分模式检测。
- 公开挑战机制允许外部反证。

## 10. Asset Lifecycle

FreshBench 的题库不是越大越好，而是保持新鲜、有效、可区分。

每个资产有生命周期：

```text
candidate -> verified -> active -> saturated -> retired
```

状态说明：

- candidate：矿工刚提交，等待验证。
- verified：通过基础验证，获得小额奖励。
- active：进入正式评测池，按使用表现释放奖励。
- saturated：被模型普遍学会，区分度下降。
- retired：泄露、过时、被挑战成功或不再有评测价值。

这让 FreshBench 不只是积累题库，而是维护一个动态更新的 AI 能力测量市场。

## 11. Demo Plan

黑客松期间可以展示一个最小闭环。

### Demo 场景

以文档结构化提取或代码题为第一类 demo。

推荐使用文档结构化提取，因为 ground truth 清楚、展示直观：

1. 输入一张发票、合同片段或财报表格图片。
2. 矿工提交一个新评测样本，包括文档、目标 JSON、字段说明和答案。
3. Validator 检查 schema、答案字段、相似度和难度。
4. Validator 用多个 baseline extractor 测试该样本。
5. 系统给出 asset score。
6. 展示题目进入 active pool 或被拒绝的原因。

### Demo 输出

可以展示：

- Miner submission JSON。
- Validator scoring report。
- Model panel results。
- Challenge case 示例。
- Asset lifecycle 状态变化。

5 到 7 分钟 pitch 中，重点展示一件事：

> FreshBench 能把一道新评测题从提交、验证、校准、挑战到奖励，变成一套可复现的市场流程。

## 12. Roadmap

### Phase 1: Hackathon Prototype

- 支持一种题型，例如文档结构化提取。
- 实现基础提交格式。
- 实现 schema check、exact match/F1、简单 novelty check。
- 展示 model panel calibration 的模拟结果。
- 输出 validator scoring report。

### Phase 2: Testnet

- 支持多矿工提交。
- 增加历史提交去重。
- 增加公开 challenge 流程。
- 增加 delayed reward 和 miner reputation。
- 支持更多题型：coding、RAG、tool-use。

### Phase 3: Production Subnet

- 接入真实 AI 评测平台或企业客户。
- 开放 benchmark asset marketplace。
- 支持外部客户购买 fresh evaluation packs。
- 按客户使用量为高质量题目提供额外奖励。
- 建立跨领域、跨语言、跨任务类型的动态评测池。

## 13. Pitch Summary

AI 模型越来越会考公开试卷，但真实能力并没有同等提升。FreshBench 解决的是 AI 评测的保鲜问题。

它不是一个静态题库，而是一个去中心化 benchmark asset 市场：

- 矿工生产新鲜评测任务。
- 验证者确认答案正确、题目新颖、难度合理、能区分模型能力。
- 挑战者帮助清理错误和污染题。
- 买家获得持续更新、可验证、可复现的评测资产。

FreshBench 的核心原则是：

> We do not reward more questions. We reward questions that remain useful after verification, calibration, challenge, and real-world use.
