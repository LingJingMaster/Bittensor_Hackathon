# FreshBench 技术栈搭建建议

整理时间：2026-05-23

目标不是一开始就做一个完整 production subnet，而是先做出能被评委理解的最小闭环：矿工提交 benchmark asset，验证者跑多阶段检查，系统输出可解释评分和生命周期状态。

## 结论先行

推荐技术栈：

| 层 | Hackathon 选择 | 后续扩展 |
| --- | --- | --- |
| Subnet / SDK | Python + Bittensor SDK v10 | 接入真实 testnet/mainnet 权重提交 |
| API | FastAPI | 拆成 validator API、marketplace API、admin API |
| Worker | Python async task + Celery/RQ 可选 | Celery / Temporal / Arq |
| 数据库 | PostgreSQL | PostgreSQL + TimescaleDB 记录评测历史 |
| 相似度检索 | pgvector 或 Qdrant | Qdrant / Milvus + embedding cache |
| 文件存储 | 本地 `data/assets/` | S3 / R2 / MinIO |
| 沙箱 | Docker | Firecracker / gVisor / Cloud sandbox |
| 前端 | Next.js 或 Vite React | Dashboard + marketplace + challenge UI |
| 模型面板 | LiteLLM / OpenAI-compatible API | 多供应商、多开源模型、本地 vLLM |
| 可观测性 | JSON logs + scoring report | OpenTelemetry + Prometheus/Grafana |

## 为什么这样搭

Bittensor 子网的核心在 miner/validator 机制，而 FreshBench 的核心在评测资产验证。Hackathon 期间最有价值的工程产出不是复杂 UI，而是一个可信 scoring pipeline。

因此技术栈应该围绕四件事：

1. 让 miner submission 标准化。
2. 让 validator scoring 可复现。
3. 让 novelty / contamination check 有证据。
4. 让 demo 能清楚展示 reward 为什么合理。

## 建议目录结构

```text
freshbench/
  README.md
  pyproject.toml
  apps/
    api/
      main.py
      routes/
    validator/
      pipeline.py
      scoring.py
      model_panel.py
      novelty.py
    miner/
      submitter.py
      generators/
  freshbench/
    schemas/
      asset.py
      report.py
    storage/
      db.py
      object_store.py
    sandbox/
      runner.py
    bittensor/
      neuron.py
      protocol.py
  data/
    assets/
    reports/
    fixtures/
  tests/
```

如果只是做 proposal demo，可以更轻：

```text
prototype/
  app.py
  schemas.py
  validator_pipeline.py
  sample_submissions/
  sample_reports/
  ui/
```

## 核心模块

### 1. Miner Submission Schema

用 Pydantic 定义统一提交格式，先支持一种题型，例如 document extraction。

最小字段：

- `task_id`
- `task_type`
- `prompt`
- `input_files`
- `ground_truth`
- `verification_method`
- `skill_tags`
- `difficulty_estimate`
- `source_type`
- `anti_contamination_evidence`

设计原则：schema 要稳定，字段要足够支持 validator 解释拒绝或通过的原因。

### 2. Validator Pipeline

建议做成清晰的阶段式 pipeline：

```text
submission
  -> schema_check
  -> ground_truth_check
  -> novelty_check
  -> model_panel_calibration
  -> challenge_risk_check
  -> final_score
  -> lifecycle_state
```

每一阶段都输出：

- `score`
- `pass/fail`
- `evidence`
- `reason`
- `cost_ms`

这样 pitch 时可以直接展示 scoring report，不需要口头解释太多。

### 3. Novelty / Contamination Check

Hackathon 阶段可以用三层：

- exact hash：防完全重复。
- text similarity：防轻微改写。
- embedding similarity：防语义换皮。

后续可以接入公开 benchmark 索引、网页搜索、GitHub 搜索和历史提交库。注意：novelty check 不需要一开始做到完美，但必须能展示证据链。

### 4. Model Panel Calibration

FreshBench 的差异化在这里。建议先用 3 到 5 个模型档位模拟或真实调用：

- weak baseline
- mid open-source model
- strong model
- rule-based extractor
- optional human spot-check

评分不是看某个模型答错，而是看题目是否形成合理能力梯度。最好的 demo 是展示三种样本：

- 太简单：所有模型都过，discrimination 低。
- 坏题：所有模型乱失败，validity 或 clarity 低。
- 好题：弱模型失败，中强模型分化，强模型也不总稳定。

### 5. Scoring Report

建议输出 JSON + UI 两种形式。

```json
{
  "asset_id": "freshbench_doc_001",
  "final_score": 0.73,
  "state": "active",
  "stages": [
    {"name": "schema_check", "score": 1.0, "passed": true},
    {"name": "ground_truth_check", "score": 0.94, "passed": true},
    {"name": "novelty_check", "score": 0.82, "passed": true},
    {"name": "model_panel_calibration", "score": 0.68, "passed": true}
  ],
  "reward_hint": {
    "submission_reward": 0.1,
    "usage_reward_weight": 0.73
  }
}
```

## Hackathon 实现优先级

### P0：必须做

- 一份清晰 proposal。
- 一个 submission schema。
- 一个 validator pipeline。
- 三个样例资产：好题、垃圾题、抄袭/近似题。
- 一个 scoring report 页面或 CLI 输出。

### P1：强加分

- embedding similarity 检索。
- model panel calibration 真实调用。
- Docker 沙箱跑 verification script。
- challenge case 示例：挑战成功后资产降权或 retired。

### P2：可延后

- 真正注册 subnet。
- 复杂 marketplace。
- 付费购买 benchmark pack。
- 完整链上经济模型。
- 多题型全覆盖。

## 技术路线建议

### 路线 A：最快 demo

适合 1 到 3 天：

- Python + FastAPI。
- SQLite 或 JSON 文件存储。
- 本地 embedding 模型或简单 TF-IDF。
- CLI/网页展示评分报告。
- Bittensor 逻辑写成模拟接口。

优点：快，风险低，适合黑客松 pitch。

缺点：不像真实 subnet，需要在文档里解释后续如何接入 Bittensor。

### 路线 B：更像真实 subnet

适合 1 到 2 周：

- Python + Bittensor SDK。
- miner / validator 分进程。
- PostgreSQL + pgvector。
- Docker sandbox。
- validator 定期拉取 miner submissions 并计算 weights。

优点：更接近真实部署，技术可信度强。

缺点：工程量更大，容易被环境和链上细节拖慢。

### 路线 C：产品化展示

适合 pitch 很看重用户体验时：

- Next.js dashboard。
- FastAPI backend。
- PostgreSQL / Qdrant。
- 展示 active pool、challenge、model panel、marketplace。

优点：评委容易理解。

缺点：如果 validator 逻辑不扎实，会显得像普通 SaaS。

## 推荐选择

当前推荐：路线 A + 局部路线 B。

也就是：先做完整 validator demo，再在代码结构和文档里预留 Bittensor SDK 接入点。这样既能把核心机制讲清楚，也不会被 testnet、钱包、注册、节点运行这些重工程细节拖住。

## 关键技术风险

| 风险 | 表现 | 应对 |
| --- | --- | --- |
| validator 成本过高 | 每道题都调用多个模型，demo 慢且贵 | 分阶段 funnel，先 cheap checks，再 model panel |
| novelty check 不可信 | 换皮题漏过 | hash + text + embedding + challenge 组合 |
| ground truth 错误 | 好题被错杀或坏题进池 | 多 solver / 多 extractor / 人工抽检高分资产 |
| scoring 太主观 | 评委质疑 reward 可刷 | 每阶段输出证据，尽量用确定性指标 |
| 过早链上化 | 时间花在钱包、节点、注册 | Hackathon 先模拟 weights，后续接 SDK |
| UI 喧宾夺主 | 看起来像评测 SaaS，不像 subnet | pitch 重点回到 commodity、miner、validator、reward |

## 下一步

建议先开工这三个 artifact：

1. `schemas.AssetSubmission`：定义矿工提交。
2. `validator_pipeline.py`：返回结构化 scoring report。
3. `demo_cases/`：准备好题、坏题、近似题三个样例。

有了这三个东西，FreshBench 的机制就能跑起来，后续再决定要不要接真实 Bittensor SDK、前端 dashboard 或沙箱执行。

