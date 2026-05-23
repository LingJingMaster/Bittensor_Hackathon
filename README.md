# FreshBench: Bittensor Hackathon Demo

整理时间：2026-05-23

FreshBench 是一个面向 AI benchmark 保鲜的 Bittensor 子网方案。它的核心不是“多出题”，也不是“做一个文档 OCR/抽取模型”，而是把高质量评测任务包装成可验证、可校准、可挑战、可长期使用的 `benchmark assets`。

第一版工程目标是做一个 Railway 可访问的单服务 demo，展示完整 validator loop：

```text
Miner submits benchmark asset
  -> schema check
  -> ground truth check
  -> novelty check
  -> model panel calibration
  -> scoring report
  -> asset lifecycle state
```

## 项目真相

FreshBench 的商品是 `benchmark asset`，不是普通题目数量。

一个 benchmark asset 至少包含：

- 评测任务本体
- 可验证答案或验证脚本
- 能力标签
- 难度估计
- 新颖性证据
- 评分证据和 validator report

V1 demo 选择“文档结构化提取”作为第一个题型，只是因为它的 ground truth 最清楚、最适合 5-7 分钟演示。请不要把 FreshBench 理解成文档抽取产品、OCR 产品或垂直模型市场。

## 非目标

当前阶段不要做这些事：

- 不做完整生产级 Bittensor 子网。
- 不接真实链上权重提交。
- 不训练模型。
- 不做 OCR 模型或文档抽取模型。
- 不把题目数量当作奖励目标。
- 不在 Railway 上跑本地大模型。
- 不把 Docker 沙箱作为 P0。
- 不先做复杂 marketplace、支付或用户系统。

## 文档地图

开工前请按顺序阅读：

| 文档 | 用途 | 阅读顺序 |
| --- | --- | --- |
| [PLAN.md](PLAN.md) | FreshBench 实施阶段、协作规则和实时进度看板 | 1 |
| [RULES.md](RULES.md) | ARM macOS + x86 Windows + Railway 的跨平台协作规则 | 2 |
| [plan_lingjing.md](plan_lingjing.md) | LingJing 的个人执行计划：validator pipeline、UI、协作边界 | 3 |
| [plan_tina.md](plan_tina.md) | Tina 的个人执行计划：storage、demo assets、API、Railway 部署 | 4 |
| [docs/freshbench-implementation-guide.md](docs/freshbench-implementation-guide.md) | 单服务 Demo 的详细工程实施手册：模块、API、验证、Railway 部署 | 5 |
| [docs/freshbench-proposal.md](docs/freshbench-proposal.md) | FreshBench 子网方案正文：问题、商品、角色、验证、奖励、反作弊、demo、roadmap | 6 |
| [docs/technical-stack.md](docs/technical-stack.md) | Hackathon 原型和后续 testnet/production 的技术栈建议 | 7 |
| [docs/official-resources.md](docs/official-resources.md) | 官方入口、文档、GitHub、TaoStats 和调研时应看的页面 | 8 |
| [docs/hackathon-idea-references.md](docs/hackathon-idea-references.md) | 往届获奖 proposal 的模式拆解 | 9 |

## 当前 V1 范围

V1 demo 只做一个最小闭环：

1. 定义 miner submission schema。
2. 准备三个样例 benchmark assets：
   - 好样例：应该进入 `active`。
   - 坏样例：ground truth 或表述有问题，应该 `rejected`。
   - 近似/换皮样例：novelty 分数低。
3. 实现 validator scoring pipeline：
   - schema check
   - ground truth check
   - novelty check
   - model panel calibration
4. 输出 scoring report：
   - stage results
   - final score
   - reward hint
   - lifecycle state
5. 用 FastAPI 提供 API 和静态 demo 页面。
6. 部署到 Railway，给评委一个公开 URL。

## 技术决策

V1 采用：

- Python 3.11+
- `uv` 管理依赖
- FastAPI 单服务
- FastAPI 静态页面作为 demo UI
- JSON 文件存储
- mock Bittensor weights
- mock/轻量 baseline model panel
- Railway 部署

后续可以升级为：

- Vite/React 前端
- PostgreSQL + pgvector
- 真实 model panel
- challenge workflow
- Bittensor SDK miner/validator 集成
- 独立 validator worker

详细方案见 [docs/freshbench-implementation-guide.md](docs/freshbench-implementation-guide.md) 和 [docs/technical-stack.md](docs/technical-stack.md)。

## API Contract

V1 API contract 固定如下，后续前后端分离也不应随意改动：

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Railway 和本地健康检查 |
| `POST` | `/api/assets/validate` | 输入 `AssetSubmission`，返回 `ScoringReport` |
| `GET` | `/api/reports` | 列出已保存 reports |
| `GET` | `/api/reports/{asset_id}` | 读取单个 report |
| `GET` | `/api/demo/samples` | 列出演示样例 |

## 协作方式

LingJing 和 Tina 分工如下：

- LingJing：validator pipeline、static demo UI、机制解释。
- Tina：JSON storage、demo assets、FastAPI API、Railway deployment。
- Phase 0 和 Phase 1 必须共同完成，因为它们决定项目骨架和 schema contract。
- Phase 1 完成后，双方只通过 schema、sample JSON、report JSON、API contract 对接。

重要规则：

- 每个阶段完成后必须更新 [PLAN.md](PLAN.md)。
- 开工前必须阅读 [RULES.md](RULES.md)。
- 不要只优化自己的任务，要给对方留下可继续的接口、样例和 validation evidence。
- 如果改 schema/API contract，必须同步更新 `PLAN.md`、implementation guide、tests 和个人计划。

## Railway 部署

Hackathon demo 部署平台选择 Railway，用于快速发布可公开访问的 FreshBench 原型服务。

Railway 官方文档：https://docs.railway.com/

当前定位：

- Railway 用于 demo hosting，而不是完整 production subnet 运行环境。
- 优先部署 FastAPI demo 服务，必要时再增加前端服务和 PostgreSQL。
- 模型面板不在 Railway 上运行本地大模型，优先使用 mock、轻量 baseline 或外部 API。
- 后续如果进入 hacker house，再评估独立 validator 节点、Bittensor SDK、PostgreSQL/pgvector 和沙箱环境。

## 防幻觉提醒

如果你是后续接手的 AI 或工程师，请牢记：

- FreshBench 不是 Quizlet on chain。
- FreshBench 不是文档 OCR 产品。
- FreshBench 不是让 miner 提交模型。
- FreshBench 的 miner 提交的是“用来评测模型的资产”。
- Validator 的核心价值是判断这个资产是否正确、新鲜、有区分度、可复现。
- 文档结构化提取只是第一个 demo task type，不是项目边界。
- V1 以 demo 闭环为目标，不以完整链上 production subnet 为目标。
