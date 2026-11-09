# 需求汇总索引（docs/specs/INDEX.md）

> 项目级需求总台账：所有需求编号、状态与进度的唯一汇总入口。新建需求由 `scripts/new_spec.py` 自动登记；状态变化时由各需求 README.md 维护者同步更新本表对应行。

## 需求清单

| 编号 | 需求 ID（目录名） | 标题 | 状态 | 当前阶段 | 优先级 | 最后更新 | 备注 |
|---|---|---|---|---|---|---|---|
| （示例行，建库时删除）REQ-000 | req-000-example | 示例需求 | accepted | 已归档 | P0 | 2026-01-01 | |

## 状态统计

| 状态 | 数量 |
|---|---|
| in-progress（进行中） | 0 |
| accepted（已验收） | 0 |
| 合计 | 0 |

## 状态取值

`clarifying` 需求澄清中 / `designing` 设计中（概要或详细）/ `coding` 编码实施中 / `testing` 测试验收中 / `accepted` 已验收归档

## 编号规则

- 需求编号 `REQ-{三位递增序号}`，如 REQ-001、REQ-002，全项目唯一，不复用已删除编号。
- 需求 ID（目录名）= `req-{序号}-{slug}`，如 `req-001-middleware-info-module`；slug 为需求语义短横线小写标识。
- 序号由 `scripts/new_spec.py` 读取本表自动分配，禁止手工跳号。
