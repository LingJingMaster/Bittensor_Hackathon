# Bittensor 官方资源与调研入口

整理时间：2026-05-23

这份文档把 Bittensor 子网 proposal 调研时最常用的资料入口集中放在一起。原则是：机制、部署和 SDK 以官方文档为准；子网市场数据以 TaoStats、TAO.app 等 dashboard 交叉查看；代码实现以 OpenTensor / Latent 的开源仓库为准。

## 第一优先级

| 资源 | 链接 | 用途 |
| --- | --- | --- |
| Bittensor 官网 | <https://bittensor.com> | 项目主站，适合看白皮书、博客、公告、生态入口和 Discord |
| 官方文档 | <https://docs.learnbittensor.org> | 最权威的学习入口，覆盖 Bittensor 架构、子网、矿工、验证者、BTCLI、SDK、Subtensor 节点 |
| SDK 仓库 | <https://github.com/opentensor/bittensor> | Bittensor Python SDK，写 miner、validator、查询 Subtensor 时优先看 |
| Subtensor 仓库 | <https://github.com/opentensor/subtensor> | Bittensor 链层代码，理解 runtime、pallet、extrinsic、节点运行方式时看 |
| TaoStats | <https://taostats.io> | 常用 dashboard，用来看 subnet alpha 价格、emission、stake、miner/validator 构成 |

## 机制理解必读

| 主题 | 链接 | 重点问题 |
| --- | --- | --- |
| Understanding Subnets | <https://docs.learnbittensor.org/subnets/understanding-subnets> | 子网是什么，miner/validator 如何围绕数字商品竞争，emission 如何分配 |
| Understanding Incentive Mechanisms | <https://docs.learnbittensor.org/learn/anatomy-of-incentive-mechanism> | 子网如何定义矿工任务、验证者评分和奖励逻辑 |
| Understanding Neurons | <https://docs.learnbittensor.org/learn/neurons> | miner、validator、axon、dendrite、metagraph、subtensor 的关系 |
| Emission | <https://docs.learnbittensor.org/learn/emissions> | TAO / alpha emission、子网权重和奖励分配逻辑 |
| Yuma Consensus | <https://docs.learnbittensor.org/learn/yuma-consensus> | 验证者权重如何汇总，最终如何影响矿工奖励 |

## 开发与部署入口

| 主题 | 链接 | 用途 |
| --- | --- | --- |
| Mining in Bittensor | <https://docs.learnbittensor.org/miners> | 了解 miner 注册、UID、axon 暴露、deregistration、immunity period |
| Validating in Bittensor | <https://docs.learnbittensor.org/validators> | 了解 validator 如何评分矿工并上链提交 weights |
| Create a Subnet | <https://docs.learnbittensor.org/subnets/create-a-subnet> | 理解创建子网的流程和参数 |
| Local Development | <https://docs.learnbittensor.org/local-build/deploy> | 本地链、测试、开发环境相关 |
| Bittensor Python SDK Docs | <https://docs.learnbittensor.org/python-api/html/> | SDK API 参考，当前官方文档页面标注为 SDK v10 |
| BTCLI Reference | <https://docs.learnbittensor.org/btcli> | 钱包、注册、子网查询、staking 等命令行操作 |

## 数据与市场观察

| 资源 | 链接 | 适合看什么 |
| --- | --- | --- |
| TaoStats Subnets | <https://taostats.io/subnets> | 每个 subnet 的 alpha、emission、stake、validator/miner 分布 |
| TaoStats Docs | <https://docs.taostats.io> | TaoStats API、emission、staking、dashboard 指标解释 |
| TAO.app Subnets | <https://tao.app/subnets> | 子网列表、项目入口、代码仓库链接 |

## 调研时的检查清单

看一个子网或 proposal 时，至少回答这些问题：

- 商品是什么：矿工到底生产什么可比较、可出售、可复用的数字商品？
- 验证者怎么评估：输入、输出、评分函数、隐藏测试、成本控制是否具体？
- 反作弊怎么做：抄袭、过拟合、探测隐藏环境、validator/miner 串通如何防？
- 数据从哪里来：ground truth、held-out set、公开随机性、历史提交如何管理？
- 谁会付钱：除了 emission，真实买家是谁，为什么需要这个 subnet？
- 技术闭环是否能 demo：5 到 7 分钟内能否展示 miner submission -> validator score -> reward/lifecycle？
