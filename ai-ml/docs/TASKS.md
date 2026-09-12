# AutoFlow AI — AI/ML Implementation Tasks and Exit Gates

**Status:** living backlog for the AI/ML subsystem
**Convention:** phases here mirror the master implementation phase plan
(Phase 0 = repo audit; Phase 1 = contracts; …). Each phase must be runnable
and tested from the CLI before the next begins.

---

## Phase 1 — Contract layer ✅ (implemented)

- [x] Scaffold `ai-ml/` package with `uv` (`pyproject.toml`, `src/` layout,
      `tests/`, pytest config).
- [x] Enums (`schemas/enums.py`): risk, model role/modality/deployment/health,
      agent kind, action type, execution/step status, verification, recovery,
      approval, memory, trust, artifact, trigger, event, actor.
- [x] Common base (`schemas/common.py`): `AutoFlowModel` (extra=forbid,
      validate_assignment), `VersionedModel`, deterministic `to_json` /
      `canonical_dict` / `compute_hash`, ID validation, `Tenancy`,
      `Principal`, `Reference`, `Timestamped`.
- [x] ~33 versioned contracts across models, tools, tasks/planning, agents,
      knowledge/context/memory, execution/observation/verification/recovery,
      approvals, workflows/artifacts/automation, events/audit.
- [x] DAG validation (no cycles, valid refs, unique ids, no dup edges,
      topological order).
- [x] Approval binding to exact plan version + action hash.
- [x] Tool argument validation against a JSON-Schema subset.
- [x] Execution state-machine transition table.
- [x] Secret-leak guard on event payloads.
- [x] Headless CLI: `version`, `contracts list`, `contracts check`,
      `phase status`, `eval smoke`.
- [x] Rigorous test suite (95 tests, 97% coverage) + CLI self-checks.

**Exit gate (met):** invalid plans/tools/workflows/approvals are rejected;
all contracts serialize/deserialize deterministically; `autoflow contracts
check` and `autoflow eval smoke` pass; `uv run pytest` is green.

---

## Phase 2 — Model gateway (next)

- [ ] `ModelProvider` protocol + adapter interface (`chat`/`stream`/`embeddings`/`health`).
- [ ] `ModelRegistry`, `CapabilityMatcher`, `ModelRouter` (capability + policy + health/latency/cost).
- [ ] `ModelHealthMonitor`, `ModelCallPolicy`, `StructuredOutputAdapter`.
- [ ] Controlled fallback, timeout handling, malformed-output rejection.
- [ ] Secret isolation (never in renderer/prompts/logs).
- [ ] CLI: `autoflow model list|route`.

**Exit gate:** model selectable by capability; provider failure → controlled
fallback; timeout handled; malformed response rejected; structured output
validated; credentials never leaked.

---

## Phase 3 — Context engine

- [ ] `ContextAssembler`, `ContextBudgetManager`, `ContextRanker`,
      `ContextSanitizer`, `ContextSerializer`.
- [ ] Ordered sections, ACL enforcement, token budgeting, untrusted separation.

## Phase 4 — ChromaDB + knowledge

- [ ] Ingestion (parse/chunk/metadata/embed), retrieval with ACL filter,
      provenance, rerank interface, deduplication, evidence packaging.

## Phase 5 — Memory

- [ ] Session/enterprise/workflow/graph memory; promotion lifecycle;
      only verified workflows become canonical.

## Phase 6 — Request normalizer

- [ ] `IntentNormalizer` → `NormalizedTask`.

## Phase 7 — Planner

- [ ] Planner agent → `TaskGraph`; deterministic plan validation.

## Phase 8 — Agent system

- [ ] Shared agent runtime; specialist profiles; dynamic assignment.

## Phase 9 — Execution agent

- [ ] State-driven next-action proposal within policy.

## Phase 10 — Tool calling

- [ ] `ToolRegistry`, `ToolSchemaValidator`, `ToolSelector`,
      `ArgumentValidator`, `ConfidenceGate`, `ToolPermissionResolver`.

## Phase 11 — Deterministic tool runtime

- [ ] Files/documents/browser/desktop/code/communication/knowledge tools
      behind deterministic adapters with observation + verification.

## Phase 12 — Computer/browser abstraction

- [ ] Semantic targets, resolution hierarchy, visual grounding fallback.

## Phases 13–19

- [ ] Document workflow E2E; email approval workflow E2E; approval engine;
      verification; recovery/replanning; semantic workflow generation;
      automation engine.

## Phases 20–24

- [ ] Backend integration; databases; event system; test environments;
      evaluation/stress harness (golden + adversarial + chaos).

---

## Standing rules for every phase

1. Models propose; deterministic runtime executes; verifiers confirm.
2. No tool outside the registry; deny-by-default permissions.
3. Every material step verified; tool success ≠ business success.
4. Approval binds to exact plan/action version.
5. Bounded autonomy — no infinite loops.
6. Runs headlessly from the CLI; every behavior has tests.
7. Never fake an integration; never report unexecuted tests as passing.
