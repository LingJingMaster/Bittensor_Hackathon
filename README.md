# Bittensor Hackathon Notes

整理时间：2026-05-23

这个文件夹目前用于整理 Bittensor 子网 proposal、官方资料、往届获奖模式和技术栈讨论。当前主线 idea 是 FreshBench：一个面向 AI benchmark 保鲜的 Bittensor 子网。

## 文档地图

| 文档 | 用途 | 阅读顺序 |
| --- | --- | --- |
| [PLAN.md](PLAN.md) | FreshBench 实施阶段、协作规则和实时进度看板 | 1 |
| [plan_lingjing.md](plan_lingjing.md) | LingJing 的个人执行计划：validator pipeline、UI、协作边界 | 2 |
| [plan_tina.md](plan_tina.md) | Tina 的个人执行计划：storage、demo assets、API、Railway 部署 | 3 |
| [docs/freshbench-implementation-guide.md](docs/freshbench-implementation-guide.md) | 单服务 Demo 的详细工程实施手册：模块、API、验证、Railway 部署 | 4 |
| [docs/freshbench-proposal.md](docs/freshbench-proposal.md) | FreshBench 子网方案正文：问题、商品、角色、验证、奖励、反作弊、demo、roadmap | 5 |
| [docs/technical-stack.md](docs/technical-stack.md) | Hackathon 原型和后续 testnet/production 的技术栈建议 | 6 |
| [docs/official-resources.md](docs/official-resources.md) | 官方入口、文档、GitHub、TaoStats 和调研时应看的页面 | 7 |
| [docs/hackathon-idea-references.md](docs/hackathon-idea-references.md) | 往届获奖 proposal 的模式拆解 | 8 |

## 当前方向

FreshBench 的核心商品不是题目数量，而是经过验证、校准、挑战，并能长期保持评测价值的 benchmark assets。

推荐优先做一个最小可演示闭环：

1. 选择一种题型：文档结构化提取。
2. 定义 miner submission schema。
3. 实现 validator scoring pipeline：schema check、ground truth check、novelty check、model panel calibration。
4. 输出 scoring report 和 asset lifecycle 状态。
5. 在 pitch 中说明它如何扩展成真实 Bittensor 子网。

## 技术决策摘要

Hackathon 阶段不建议一开始就把所有链上、市场、支付和复杂前端都做满。更稳的路线是：

- Python 作为核心语言，贴近 Bittensor SDK、validator/miner 生态和评测脚本。
- FastAPI 提供 demo API。
- PostgreSQL 存结构化数据，pgvector 或 Qdrant 做相似度检索。
- Docker 沙箱运行 scoring script、代码题或 tool-use 任务。
- 简洁前端展示 miner submission、validator report、model panel 和生命周期。

详细方案见 [docs/technical-stack.md](docs/technical-stack.md)。

## 部署选择

Hackathon demo 部署平台选择 Railway，用于快速发布可公开访问的 FreshBench 原型服务。

Railway 官方文档：https://docs.railway.com/

当前定位：

- Railway 用于 demo hosting，而不是完整 production subnet 运行环境。
- 优先部署 FastAPI demo 服务，必要时再增加前端服务和 PostgreSQL。
- 模型面板不在 Railway 上运行本地大模型，优先使用 mock、轻量 baseline 或外部 API。
- 后续如果进入 hacker house，再评估独立 validator 节点、Bittensor SDK、PostgreSQL/pgvector 和沙箱环境。
