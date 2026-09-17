# Synthetic-Life — Current Status

## Current accepted state

**v0.7.5 — FROZEN**  
Commit: `26b1308f3e61ca1d9fe573e693748021831a816d`

v0.7 — cleanup/refactor line. Она не добавляла новую cognitive capability и
сохранила frozen behavior v0.7.0/v0.6.6. Полный cross-worktree audit после
Python/C++ structural refactor и tooling cleanup не обнаружил semantic, numeric,
causal, persistence или ABI divergence.

Полный evidence:
[`docs/V0_7_5_REGRESSION_AUDIT.md`](docs/V0_7_5_REGRESSION_AUDIT.md).

## Acceptance snapshot

Последний полный audit:

```text
pytest                         422 passed
CTest Release                  2/2 passed
historical groups v0.2-v0.6.6 17/17 PASS
full_graph_sync_calls          0
```

Canonical workload, seed `6607`:

```text
digest          7d80bffa82cfbabf8d11373883d03056b26b27eb53a4cbe9246a666e079fbb0f
actions         79
scheduler       655 events
queue peak      3
Cognits         27
Relations       162
planner cycles  294
FFI calls       2668
Assemblies      6
```

`PYTHONHASHSEED=1` и `777` совпадают. Семь запусков v0.7.0 и семь запусков
v0.7.5 совпали по digest, structural counters и full neural telemetry.

## Long-life state

Проверенный manual run: `1,000 WorldTime`.

```text
actions               6,666
scheduler events      54,363
queue peak            3
Cognits               593
Relations             16,384 (global cap)
Assemblies            87
neural events          95,129
planner cycles         25,329
full_graph_sync_calls  0
```

Relations достигли cap к `WorldTime 300` и оставались bounded ещё 700 WorldTime,
при этом actions, cognition, neural events и Assemblies продолжали изменяться.
NaN/Inf, capacity overflow и scheduler runaway не обнаружены.

50,000-WorldTime soak не запускался: 1,000 WorldTime заняли `548.725 s`.
Это зафиксированная audit limitation, а не скрытый PASS.

## Performance audit

Одинаковый canonical workload, одна машина, семь запусков каждой версии:

| Version | Median | Range |
|---|---:|---:|
| v0.7.0 `e97a7b7` | 0.282944 s | 0.276895–0.293184 s |
| v0.7.5 audited implementation | 0.278439 s | 0.272324–0.289722 s |

Delta `-1.59%` классифицирована как wall-clock noise. Native benchmark дал
смешанные отклонения в обе стороны без repeatable regression; workload/memory
counters совпадали.

## Current production architecture

```text
main.py
  -> ContinuousRuntime
  -> Simulation(backend="native")
  -> NativeWorldFacade -> C++ WorldRuntime
  -> SyntheticEntityCore -> NativeGraphBackend -> C++ NativeBrainEngine
  -> NeurodynamicSubstrate
  -> EventScheduler
  -> NativeObserver (read-only)
```

Authority summary:

- Python: semantic cognition, memory/planner/language, cognition frontier;
- C++: authoritative numeric Cognit/Relation graph, World, scheduler,
  micro-neural substrate, Assemblies and one-way bridge;
- Python graph/World: reference/oracle/compatibility;
- observer: snapshot-only.

Полное описание: [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Persistence

Текущие accepted surfaces:

```text
.sebrain v6
.seworld v7
native graph v3
```

Existing migration/checksum/roundtrip/exact-continuation tests PASS. В
репозитории нет отдельного внешнего архивного binary fixture старых
`.sebrain/.seworld`; это вторая явно зафиксированная limitation v0.7.5.

## Frozen milestone summary

| Milestone | Status | Purpose |
|---|---|---|
| v0.7.0 | FROZEN | baseline/full architecture audit |
| v0.7.1 | FROZEN | readability/documentation foundation |
| v0.7.2 | FROZEN | Python structural extraction |
| v0.7.3 | FROZEN | C++ structural extraction |
| v0.7.4 | FROZEN | repository/tests/tooling |
| v0.7.5 | FROZEN | full regression/performance audit |
| v0.7.6 | PLANNED | architecture freeze/future-proofing |

Historical v0.2-v0.6.6 acceptance сохраняется как executable regression layer;
точная taxonomy — в [`docs/TESTING.md`](docs/TESTING.md).

## Next work

### v0.7.6 — Architecture Freeze and Future-Proofing

Остаётся финальный cleanup:

- удалить только доказанный dead code;
- окончательно маркировать legacy/reference paths;
- усилить future-proof architecture guards;
- сверить docs с фактической структурой;
- проверить clean-clone build/verify path;
- заморозить public/internal boundaries перед новой capability work.

### v0.8 — Homeostatic Motivation and First Survival Learning

Запланировано, но **не реализовано**. Основная исследовательская цепочка:

```text
physiological deviation
-> non-semantic interoception
-> learned representation/consequence
-> prediction
-> planner trajectory valuation
-> Action
-> physical/physiological consequence
-> changed future behavior
```

Подробный план и архитектурные контракты — в [`ROADMAP.md`](ROADMAP.md).

## Documentation rule

Этот файл содержит только **текущее** состояние. Старые version-by-version
подробности находятся в `ROADMAP.md`, experiment reports и frozen audit
documents; они больше не копируются сюда, чтобы не создавать противоречащие
снимки прошлого.
