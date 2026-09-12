# AutoFlow AI — AI/ML Core

The headless intelligence and execution core of AutoFlow AI. It runs and is
fully testable **without** the desktop client (Electron), through a Python API,
a CLI, and an automated test suite.

See `docs/` in this folder for the engineering specification. See
`../docs/IMPLEMENTATION_STATUS.md` for the current build phase.

## Requirements

- Python >= 3.11 (developed/verified on 3.14)
- [uv](https://docs.astral.sh/uv/) for environment + dependency management

## Setup (local)

```powershell
# from ai-ml/
uv venv
uv pip install -e ".[dev]"
```

## Run the CLI

The entire subsystem is drivable from the command line:

```powershell
# show versions
uv run autoflow version

# list every contract model
uv run autoflow contracts list

# build + JSON round-trip every contract (self-check)
uv run autoflow contracts check

# fast end-to-end contract smoke test (plan -> tool -> verify -> approval)
uv run autoflow eval smoke

# show the current implementation phase
uv run autoflow phase status
```

Each command exits non-zero on failure, so it can gate CI.

## Run the tests

```powershell
uv run pytest            # full suite
uv run pytest -m contract  # contract tests only
uv run pytest --cov        # with coverage
```

## Layout

```text
ai-ml/
├── pyproject.toml
├── src/autoflow_ai/
│   ├── schemas/         # Phase 1 — versioned Pydantic contracts
│   ├── samples.py       # canonical valid instances (fixtures + CLI self-check)
│   └── cli.py           # headless CLI entry point (`autoflow`)
├── tests/               # rigorous contract/unit tests
└── docs/                # AI/ML engineering documentation
```

## Phase status

- **Phase 1 (Contract layer):** implemented — ~33 versioned contracts, DAG
  validation, approval binding, tool-argument validation, execution state
  machine, secret-safe events. Verified by the test suite and
  `autoflow contracts check` / `autoflow eval smoke`.
