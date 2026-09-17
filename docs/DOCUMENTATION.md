# Synthetic-Life Documentation Map

Цель этого файла — не допустить повторного дрейфа документации. У каждого
документа одна основная роль.

## Living documents

| Document | Role | Update when |
|---|---|---|
| [`../README.md`](../README.md) | вход в проект | меняется current release/setup/navigation |
| [`../CURRENT_STATUS.md`](../CURRENT_STATUS.md) | только актуальный accepted state | milestone accepted/rejected |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | фактическая текущая architecture | меняется ownership/boundary/dataflow |
| [`../DEVELOPER_GUIDE.md`](../DEVELOPER_GUIDE.md) | developer workflow | меняется build/test/code ownership workflow |
| [`../ROADMAP.md`](../ROADMAP.md) | history + future milestones | планируется/закрывается milestone |
| [`TESTING.md`](TESTING.md) | verification contract | меняются tests/guards/gates |

Эти документы должны согласовываться между собой. Они не должны копировать
полный version history друг у друга.

## Frozen v0.7 evidence

- [`V0_7_REFACTOR_CONTRACT.md`](V0_7_REFACTOR_CONTRACT.md) — frozen baseline,
  ownership, ID/wire/persistence/refactor contract для линии v0.7.
- [`V0_7_5_REGRESSION_AUDIT.md`](V0_7_5_REGRESSION_AUDIT.md) — фактический
  cross-worktree regression/performance audit.
- [`V0_7_6_ARCHITECTURE_FREEZE.md`](V0_7_6_ARCHITECTURE_FREEZE.md) — финальная
  classification, clean-clone validation и frozen architecture baseline.

Это evidence documents. После freeze их не переписывают для косметической
актуализации; новые факты добавляются отдельным документом/milestone.

## Current v0.8 design

- [`V0_8_HOMEOSTASIS_DESIGN.md`](V0_8_HOMEOSTASIS_DESIGN.md) — physiology
  ownership/model, persistence, causal seams and staged v0.8.x integration.

## Foundational / historical design documents

- [`../COGNITIVE_FORMALISM.md`](../COGNITIVE_FORMALISM.md) — формализм v0.4,
  фундамент для части текущей cognition, но не полное описание v0.6/v0.7.
- [`../DESIGN_DECISIONS.md`](../DESIGN_DECISIONS.md) — historical decision log
  через ранние версии; старые schema/benchmark statements читаются в контексте
  соответствующей версии.
- [`../ARCHITECTURE_RU.md`](../ARCHITECTURE_RU.md) — compatibility pointer на
  canonical `ARCHITECTURE.md`, отдельная копия больше не поддерживается.

## Historical experiment/report artifacts

Не являются current status:

```text
V0_2_EXPERIMENT_REPORT.md
V0_3_EXPERIMENT_REPORT.md
V0_4_EXPERIMENT_REPORT.md
V0_5_1_EXPERIMENT_REPORT.md
V0_5_2_HYBRID_REPORT.md
V0_5_3_CONTINUOUS_RUNTIME_PLAN.md
```

Они сохраняются как воспроизводимость/история и не переписываются только потому,
что архитектура ушла вперёд.

## Authority order

Если документы расходятся:

1. executable tests / deterministic oracle;
2. frozen version-specific contract/audit для соответствующего milestone;
3. `ARCHITECTURE.md` для текущей architecture;
4. `CURRENT_STATUS.md` для current acceptance state;
5. `ROADMAP.md` для future plan;
6. historical reports для исторического context.

## Documentation update rule

Architecture-changing commit должен ответить:

- изменился ли state owner;
- изменился ли causal/data boundary;
- изменился ли ID/time domain;
- изменился ли persistence/wire format;
- какие tests/guards защищают новый contract.

Если хотя бы один ответ «да», обновите `ARCHITECTURE.md`,
`DEVELOPER_GUIDE.md`/`TESTING.md` при необходимости и milestone state в
`CURRENT_STATUS.md`/`ROADMAP.md`.

Не добавляйте version-by-version changelog в `README.md` или
`CURRENT_STATUS.md`: для этого существуют `ROADMAP.md` и frozen reports.
