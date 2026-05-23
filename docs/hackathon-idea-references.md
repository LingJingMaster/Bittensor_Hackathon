# 黑客松往届获奖 Idea 参考

整理时间：2026-05-23

相关文档：

- [FreshBench 子网方案正文](freshbench-proposal.md)
- [技术栈搭建建议](technical-stack.md)
- [Bittensor 官方资源与调研入口](official-resources.md)

这份文档整理了几份往届黑客松获奖 proposal，用于后续做 Bittensor / subnet 相关 idea 时参考。重点不是复述项目内容，而是提炼它们为什么像一个“好子网”：商品定义清楚、矿工产出可比较、验证机制具体、反作弊设计扎实，并且有真实市场牵引。

## 参考项目总览

| 项目 | 一句话 | 核心商品 | 为什么适合 Bittensor |
| --- | --- | --- | --- |
| [Defektr](https://www.notion.so/Defektr-docs-321289de875980c78023d13fbba8c6b9) | 面向制造业质检的去中心化视觉模型子网 | 可部署到边缘设备的缺陷检测模型 | 矿工竞争训练模型，验证者用统一数据集评估准确率、速度、鲁棒性，工厂采购最佳模型 |
| [Proven](https://drive.google.com/file/d/18bXTxQ5NvdK9MkTc_QmOxCPTtbdaofc9/view) | 面向 AI 代码时代的软件验证子网 | 自动生成高覆盖率 E2E / Playwright 测试脚本 | 矿工像自动 QA 工程师，验证者用 mutation testing 检查测试是否真的能抓 bug |
| [OpenMind](https://www.notion.so/Ideathon-Submission-OpenMind-3114d0ffbf09806680cdc6ed742743c1) | 给 AI Agent 的长期记忆层 | 持久、可检索、可证明保存的 agent memory | 矿工提供向量 + 图谱检索、存储证明、重构能力，验证者测召回、忠实度、延迟、耐久性 |
| [C-SWON](https://github.com/adysingh5711/C-SWON) | "Zapier for Subnets"，跨子网工作流编排 | 最优工作流策略 / DAG | 矿工提出调用哪些子网、顺序和参数，验证者执行并按质量、成本、延迟评分 |

## 项目拆解

### Defektr：制造业视觉质检

**核心问题**

制造业质量控制成本很高，传统机器视觉系统昂贵且定制化强，中小型工厂很难负担。AI 视觉质检市场很大，但现有方案往往被 Cognex、Keyence、云厂商或专有系统锁定。

**子网商品**

生产级、边缘可部署的缺陷检测模型。模型需要能在 Jetson、Coral TPU、工业 PC 等边缘硬件上高速运行。

**矿工任务**

矿工训练并提交缺陷检测模型，例如 ONNX、TensorRT、TFLite 文件。矿工可以使用不同架构、训练数据和优化策略，目标是产生更准确、更快、更鲁棒的模型。

**验证者任务**

验证者维护 benchmark 数据集，下载矿工模型，在标准参考硬件上本地运行评估。主要指标包括：

- Accuracy：缺陷检测 F1 / segmentation 表现
- Speed：单张图推理速度
- Robustness：光照、旋转、噪声等增强条件下的稳定性

**反作弊机制**

- 验证者本地运行模型，不信任矿工自报速度
- benchmark 使用公开随机种子采样，减少提前泄露和过拟合
- 加入增强样本，打击只记住固定样本的模型
- 对输出相似度、模型权重相似度进行重复提交检测

**可借鉴点**

这是“垂直行业模型市场”的范式：把真实行业需求变成可评估的模型竞争，再用客户采购作为第二奖励信号。

### Proven：去中心化软件验证层

**核心问题**

AI 代码生成让软件生产速度变快，但验证成为瓶颈。大量代码可以被生成，却缺乏高质量、自动化、可信的测试覆盖。

**子网商品**

高覆盖率、低误报的 E2E / Playwright 测试脚本。项目把矿工定位为 adversarial QA engineers。

**矿工任务**

矿工收到软件规格、目标应用或测试环境后，生成 Playwright 测试脚本，通过 Bittensor Synapse 提交给验证者。

**验证者任务**

验证者用分阶段 funnel 控制计算成本：

- Stage 1：静态检查，排除非法或无效脚本
- Stage 2：在正确实现上运行测试，必须全部通过，避免 false positive
- Stage 3：在多个 mutated 版本上运行测试，检查脚本能杀死多少 mutants

**评分逻辑**

测试必须先通过 clean reference implementation，否则直接归零。通过后，主要根据 killed mutants 数量、执行效率、覆盖质量等计算分数。奖励设计偏 winner-takes-all 或陡峭 top-n 分布。

**反作弊机制**

- Assertion roulette：乱写断言会在 clean version 上失败，被 Pclean penalty 归零
- Hard-coded answers：验证者动态生成 mutant，避免矿工背答案
- Plagiarism：用 AST / semantic similarity 检测复制，优先奖励更早提交者
- Probing：限制脚本探测环境、DOM 或隐藏信息的行为

**可借鉴点**

这是“自动验证市场”的范式。它非常适合黑客松，因为 demo 可以做出完整闭环：生成任务、矿工产出测试、验证者注入 mutation、计算分数。

### OpenMind：AI Agent 长期记忆层

**核心问题**

现代 AI agent 受固定 context window 限制，长期对话、工具调用、项目历史和用户偏好会被压缩或丢失，导致重复解释、幻觉、成本升高和长期一致性差。

**子网商品**

持久、低延迟、高保真的外部记忆服务。它面向 MCP-compatible agents，提供跨工具、跨会话的 shared memory layer。

**矿工任务**

矿工负责存储加密上下文分片，维护混合索引，并响应检索请求：

- semantic vector search
- relational / knowledge graph traversal
- storage proof
- shard reconstruction
- MCP endpoint exposure

**验证者任务**

验证者通过真实 MCP query、合成 query、storage challenge、adversarial query 来评价矿工：

- retrieval relevance
- fidelity to original data
- reconstruction accuracy
- p95 latency
- durability proof
- graph reasoning depth
- downstream agent improvement

**反作弊机制**

- commit-reveal，减少抢跑或复制
- poisoned / adversarial queries，检测幻觉、篡改、陈旧数据
- storage possession challenge，证明矿工真的保存数据
- Yuma Consensus 下调异常验证者或低质量矿工

**可借鉴点**

这是“agent 基础设施”的范式。它不直接做一个聊天产品，而是把 agent 生态的底层能力商品化：记忆、检索、持久性和可验证保存。

### C-SWON：跨子网工作流编排

**核心问题**

Bittensor 有许多专业子网，但开发者缺少原生方式把多个子网组合成可靠端到端工作流。每个应用都要手动选择、串联、调参和监控多个子网。

**子网商品**

最优工作流策略：给定任务后，矿工提交调用哪些子网、以什么顺序、带什么参数的 DAG execution plan。

**矿工任务**

矿工提出 multi-subnet execution plan，包括：

- 子网选择
- 调用顺序
- 参数配置
- 成本和延迟预测
- fallback / retry 策略

**验证者任务**

验证者在沙箱 Docker 容器里执行矿工计划，根据任务成功率、输出质量、成本、延迟等进行综合评分。

**评分与反作弊**

- workflow 失败则 cost / latency 得分为 0，防止便宜但无效的方案刷分
- VRF-keyed task schedule，减少预缓存答案
- synthetic ground truth，用隐藏已知答案任务检测真实规划能力
- benchmark rotation，避免固定任务被过拟合
- deterministic scoring，尽量不用主观 LLM judge
- miner weight cap，避免单矿工垄断 emissions

**可借鉴点**

这是“Bittensor 内部组合层”的范式。它的好处是天然服务 Bittensor 生态本身，不需要一开始就寻找外部客户。

## 共同获奖模式

### 1. 商品定义清楚

优秀 proposal 不只是说“做一个 AI 应用”，而是明确这个子网生产什么可交换商品：

- Defektr：质检模型
- Proven：测试脚本
- OpenMind：长期记忆服务
- C-SWON：工作流策略

判断一个 idea 是否适合 subnet，可以先问：矿工到底在卖什么？

### 2. 矿工产出可比较

每个项目都能回答：不同矿工提交的东西，怎么排名？

好的比较方式通常满足：

- 输入一致
- 输出格式标准化
- 评分可复现
- 指标和真实价值相关
- 较少依赖主观打分

### 3. 验证机制具体

强 proposal 会写清楚验证者怎么工作，而不是停留在“validator evaluates miners”。

常见验证方式：

- held-out benchmark
- synthetic task
- mutation testing
- deterministic public randomness
- storage / possession challenge
- sandbox execution
- reference hardware evaluation
- schema validation / unit test runner

### 4. 反作弊设计扎实

评委会很在意 incentive 是否会被刷。往届项目都会主动列出攻击方式和防御。

常见攻击面：

- overfitting benchmark
- hard-coded answer
- self-reported latency fraud
- plagiarism / copy submission
- low-cost low-quality spam
- miner-validator collusion
- probing hidden environment
- cached response

### 5. 有真实市场牵引

好的子网不是只靠 emissions 空转，而是能解释未来谁会付钱：

- Defektr：工厂、系统集成商、机器人厂商
- Proven：Bittensor 开发者、Web3 协议、SaaS、AI-native 公司
- OpenMind：MCP agent、企业 assistant、research agent、long-running workflow
- C-SWON：Bittensor 应用开发者、需要多子网组合的 agent builder

## 主办方介绍内容总结

这次黑客松不是要做一个普通 Web3 应用，而是要做一个 Bittensor 子网 proposal。核心不是 UI、不是合约、也不是完整产品 demo，而是设计一个能跑得通的去中心化激励机制。

### 现在最该做的事

1. 先定一句话子网方向：你们到底想激励全球贡献者产出什么？例如更好的 coding agent、更便宜稳定的 GPU、更好的分子候选、更高质量的数据集、更强的某类模型等。

2. 明确这个子网产出的商品是什么：主办方反复强调 commodity，也就是这个子网最终向市场、研究界或生态提供什么有价值的东西。不能只是“有一堆算力，我想做点 AI”。

3. 设计三类角色：

- Miner / 贡献者：提交什么？代码、模型、数据、算力、推理服务、分子结构？
- Validator / 验证者：怎么验证？用什么 benchmark、ground truth、环境、测试集、评分函数？
- Subnet owner / 机制设计者：怎么制定规则、分配奖励、防作弊、维护增长？

4. 重点想清楚激励机制：谁拿奖励？winner-takes-all、Top K、按分数比例分配，还是多维目标？奖励必须和真实有价值的贡献绑定。

5. 重点想清楚反作弊机制：这是评委会很可能重点看的地方。要回答：

- 怎么防刷分？
- 怎么防抄袭？
- 怎么防过拟合测试集？
- 怎么防女巫攻击？
- 怎么防 Miner 钻评分规则漏洞？
- Validator 的评分是否可复现、可验证、公开透明？

6. 准备 proposal + PPT + 5 到 7 分钟 pitch。代码不是必须，但如果能写一点 validator/miner 伪代码、评分函数、测试网小 demo，会是加分项。

### 最终作品需要满足的需求

最后交的不是产品原型，而应该是一套完整的子网设计：

- 一句话介绍：这个子网做什么。
- 问题和价值：为什么这个方向值得被激励。
- 子网商品：最终产出的 commodity 是什么，谁会用，为什么有商业或研究价值。
- 为什么必须用 Bittensor：为什么不是普通创业公司、普通 SaaS、普通 Web3 app。
- Miner 任务：输入是什么，输出是什么，提交格式是什么。
- Validator 任务：怎么打分，ground truth 从哪里来，如何复现。
- 奖励机制：奖励按什么规则分配，如何推动持续改进。
- 反作弊设计：作恶路径和防御方案。
- 透明性：代码、数据、评分过程最好公开或可验证。
- Permissionless：普通贡献者能低门槛加入，而不是 owner 独裁或闭源控制。
- 工作流图：从 Miner 提交，到 Validator 评分，到奖励分发，最好画一张流程图。
- Roadmap：后续如果进入 hacker house，怎么落地到测试网或主网。

一句话版：你们要交的是“一个可被 Bittensor 生态相信的去中心化比赛规则”。谁参赛、交什么、怎么判赢、怎么防作弊、赢了为什么对世界有价值，这五件事要讲清楚。

## 后续写 Proposal 的推荐结构

可以按下面模板写黑客松 idea：

```md
# 项目名

## 1. One-liner

一句话说明这个子网解决什么问题、生产什么商品。

## 2. Problem

真实痛点是什么？为什么现在重要？现有方案哪里不够？

## 3. Subnet Commodity

这个子网生产的可竞争商品是什么？

## 4. Miner Role

矿工收到什么输入？提交什么输出？输出格式是什么？

## 5. Validator Role

验证者如何生成任务、执行评估、计算分数、提交权重？

## 6. Scoring Formula

核心指标和权重是什么？例如：

Score = 0.5 * quality + 0.3 * speed + 0.2 * robustness

## 7. Anti-Gaming

列出 3-5 种攻击方式，以及对应反制。

## 8. Market Logic

谁会使用？谁会付钱？早期如何冷启动？后期如何从 emission-driven 走向 market-driven？

## 9. Demo Plan

黑客松期间能展示的最小闭环是什么？
```

## 选题判断清单

提出一个新 idea 后，可以用这份 checklist 快速筛选：

- [ ] 是否能用一句话说清楚子网商品？
- [ ] 矿工输出是否有标准格式？
- [ ] 验证者是否能客观评估矿工输出？
- [ ] 是否有至少一个 hard benchmark 或 synthetic benchmark？
- [ ] 是否能设计 3 个以上反作弊机制？
- [ ] 是否能做出最小 subnet loop demo？
- [ ] 是否有明确早期用户？
- [ ] 是否能解释为什么中心化公司不如 subnet 适合做这件事？
- [ ] 是否存在外部收入或真实需求，而不只是吃 emissions？
- [ ] 是否能在黑客松时间内展示一个可信原型？

## 适合继续发散的方向

下面这些方向更容易继承往届获奖 proposal 的模式：

- 自动化验证：代码测试、智能合约审计、API 回归测试、浏览器操作评测
- 可信检索：企业文档 RAG 评测、长期记忆、知识图谱一致性检查
- 垂直模型市场：医疗影像、工业质检、卫星图像、金融文档解析
- Agent 基础设施：工具选择、子网路由、任务分解、workflow planning
- 数据质量市场：标注审核、数据清洗、合成数据验证、benchmark 生成
- 安全与对抗：prompt injection 检测、agent sandbox audit、web3 risk scoring

## 关键启发

黑客松里更强的 Bittensor idea 通常不是“做一个功能”，而是“把某种智能能力变成可验证、可竞争、可购买的市场”。

写 proposal 时要优先回答四个问题：

1. 矿工到底生产什么？
2. 验证者怎么知道谁更好？
3. 作弊者会怎么刷分？
4. 真实用户为什么会用它？
