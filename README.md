# Bittensor Hackathon Notes

整理时间：2026-05-23

这个文件夹目前用于整理 Bittensor 子网 proposal、官方资料、往届获奖模式和技术栈讨论。当前主线 idea 是 FreshBench：一个面向 AI benchmark 保鲜的 Bittensor 子网。

## 文档地图

| 文档 | 用途 | 阅读顺序 |
| --- | --- | --- |
| [docs/freshbench-proposal.md](docs/freshbench-proposal.md) | FreshBench 子网方案正文：问题、商品、角色、验证、奖励、反作弊、demo、roadmap | 1 |
| [docs/technical-stack.md](docs/technical-stack.md) | Hackathon 原型和后续 testnet/production 的技术栈建议 | 2 |
| [docs/official-resources.md](docs/official-resources.md) | 官方入口、文档、GitHub、TaoStats 和调研时应看的页面 | 3 |
| [docs/hackathon-idea-references.md](docs/hackathon-idea-references.md) | 往届获奖 proposal 的模式拆解 | 4 |

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

