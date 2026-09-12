# AutoFlow AI

**Turn one instruction into a verified workflow.**

AutoFlow AI is an API-first, general-purpose agentic task execution platform.
A user states an outcome once; AutoFlow plans it, retrieves authorized context,
assigns specialist agents, routes models by capability, executes controlled
tools, observes real state, verifies the outcome, recovers from failure, asks
for human approval where risk requires it, produces artifacts, and stores the
verified workflow for reuse.

It is built brain-first: the AI/ML execution core must work headlessly (via CLI
and tests) before the backend and desktop are layered on top.

## Repository layout

```text
autoflow_ai/
├── docs/       # product + system source of truth (start with PROJECT_VISION.md)
├── ai-ml/      # intelligence + execution core (headless, testable) — Python
├── backend/    # control plane: API, auth, orchestration, persistence — Python
├── desktop/    # Electron + React command center (built last)
└── README.md
```

## Where to start

- Product & architecture: `docs/PROJECT_VISION.md`, `docs/PRD.md`,
  `docs/SYSTEM_ARCHITECTURE.md`.
- Current build state and phase ledger: `docs/IMPLEMENTATION_STATUS.md`.
- AI/ML core (runnable today): `ai-ml/README.md`.

## Quick start (AI/ML core)

```powershell
cd ai-ml
uv venv
uv pip install -e ".[dev]"
uv run autoflow eval smoke   # end-to-end contract smoke test
uv run pytest                # full test suite
```

## Build order

```text
contracts → model gateway → planner → agents → tool calling → execution runtime
→ verification → recovery → knowledge/RAG/memory → stress harness → backend
→ browser/desktop automation → desktop UI → hardening
```

The platform only advances a phase when the current layer has measurable,
tested evidence that it works. Progress is tracked in
`docs/IMPLEMENTATION_STATUS.md`.
