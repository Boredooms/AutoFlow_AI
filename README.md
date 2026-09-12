# AutoFlow AI

A local, evidence-driven agentic system: from one natural-language instruction it
plans, delegates to specialists, grounds itself in RAG + memory + real web
research, operates real applications (browser/desktop) through a tool authority
chain, verifies every step with independent evidence, and only reports success
when the evidence proves it.

> **Scope:** this repository is the **local AI/ML core + a local orchestration
> API + a minimal browser frontend**. It runs entirely on localhost with no
> cloud backend required. Capabilities that need credentials or specific
> hardware (real Gmail send, real Word UI, live cloud models) are **opt-in and
> honestly labeled** — never faked.

---

## What AutoFlow does

- **Agentic runtime** — a supervisor dynamically decomposes a mission, delegates
  to capability-matched specialists (Research / Document / Computer / Browser /
  Communication / QA), and an independent critic gates completion.
- **Grounding** — RAG knowledge + workflow memory + live web research + session
  + observations are merged by an **EvidenceBroker** with trust + provenance.
  Retrieved content is always DATA, never instructions.
- **Real execution** — semantic browser/desktop control (not coordinate replay),
  multi-signal verification, bounded recovery, and approval-bound side effects.
- **Model Lab** — benchmark + score + compare configured models (NVIDIA / Qwen /
  local deterministic) structurally, with secret-free observability.
- **Simulation + live** — run the whole loop deterministically before any real
  desktop/browser/model use, then switch to live where configured.

## Architecture

```
USER
  -> FRONTEND (served at /)
  -> LOCAL API (autoflow serve, stdlib http.server)
  -> AI/ML AGENTIC RUNTIME
       Planner · Supervisor · Specialists · QA/Critic
       RAG · Workflow Memory · EvidenceBroker
       Model Gateway · Router · Tool Registry · Approval/Policy
       Execution Engine · Recovery · Vision/OpenCV · Browser/Desktop
  -> REAL OBSERVED EXECUTION -> VERIFICATION -> ARTIFACTS + AUDIT + TRACE
  -> FRONTEND REAL-TIME EVENT STREAM (SSE)
```

## Core guarantees

LLMs propose; typed schemas + policy validate; deterministic tools perform side
effects; observers inspect real state; verifiers confirm independently. Failed
verification means NOT VERIFIED — never success. Approval binds to the exact
action; any change invalidates it. Secrets never enter prompts, logs, traces,
datasets, or Git. Retrieval is not authorization; model confidence is not
verification; tool success is not task success.

## Repository structure

```
ai-ml/        the AI/ML core (installable Python package: autoflow_ai)
  src/autoflow_ai/{planning,agents,runtime,society,rag,memory,context,
                   computer_use,model_gateway,lab,server,documents,editing,schemas}
  tests/      the test suite
backend/      docs only (no separate service; the local API lives in ai-ml/server)
desktop/      docs only
docs/         project + deployment documentation
examples/     sample knowledge documents for RAG
```

## Requirements

- **Python 3.14** and [`uv`](https://docs.astral.sh/uv/) (the project manager).
- Optional: Playwright + Chromium (browser/web), `uiautomation` (Windows
  desktop), OpenCV, a configured model provider (NVIDIA / ModelScope).
- No Node/build toolchain is required — the frontend is a single static page
  served by the API.

## Quick start (Windows / PowerShell)

```powershell
cd ai-ml
uv sync                              # install deps into .venv
copy ..\.env.example ..\.env         # then edit ..\.env if you want live models
uv run python -m autoflow_ai.cli doctor       # environment diagnostics
uv run python -m autoflow_ai.cli demo         # deterministic flagship demo
uv run python -m autoflow_ai.cli serve        # http://127.0.0.1:8770
```

Then open <http://127.0.0.1:8770> and click **Run Mission** (Simulation mode).

## Quick start (Linux / macOS)

```bash
cd ai-ml
uv sync
cp ../.env.example ../.env
uv run python -m autoflow_ai.cli doctor
uv run python -m autoflow_ai.cli demo
uv run python -m autoflow_ai.cli serve
```

## Configuration

Copy `.env.example` to `.env`. Everything runs offline with the local
deterministic provider if you configure nothing. To enable a real model, set the
`PRIMARY_MODEL_*` (NVIDIA-style) and/or `SECONDARY_MODEL_*` (ModelScope/Qwen)
variables. See [`docs/MODELS.md`](docs/MODELS.md).

Key variables (full list in `.env.example`):

| Variable | Purpose |
|---|---|
| `PRIMARY_MODEL_BASE_URL/ID/API_KEY` | remote OpenAI-compatible model (NVIDIA) |
| `SECONDARY_MODEL_*` (+`_STREAMING`) | ModelScope/Qwen (streaming) |
| `AUTOFLOW_MODEL_HOME` | local model cache (default `~/.autoflow/models`) |
| `AUTOFLOW_ALLOW_WEB=1` | opt-in real web navigation |
| `AUTOFLOW_REAL_WORD=1` | opt-in real Word UI |
| `AUTOFLOW_REAL_GMAIL=1` | opt-in real Gmail (needs controlled account) |

## Model Lab

```powershell
uv run python -m autoflow_ai.cli model list
uv run python -m autoflow_ai.cli model info
uv run python -m autoflow_ai.cli model install nvidia      # reports configured/missing env keys
uv run python -m autoflow_ai.cli model lab list
uv run python -m autoflow_ai.cli model lab test model_local01
uv run python -m autoflow_ai.cli model lab benchmark
uv run python -m autoflow_ai.cli model lab compare --models nvidia,qwen,deterministic
uv run python -m autoflow_ai.cli model console
```

## On-device tool-calling agent (Cactus Needle 2)

A 45M-parameter on-device model that turns a natural-language instruction into
real tool calls (Word, notes, browser, YouTube, Gmail draft, file ops, and 20+
more). The fine-tuned weights (`my_agent.cact`, ~14MB) ship inside the package,
so nothing to download; it runs on the CPU with no API key and no cloud.

```powershell
uv pip install cactus-needle                       # one-time (optional extra)
# plan only (safe, no side effects):
uv run python -m autoflow_ai.cli needle run "write hi my name is archishman into notes.docx"
# actually perform the action on your machine:
uv run python -m autoflow_ai.cli needle run "make a note that says buy milk" --execute
```

Safe by default: without `--execute` the model selects the tool and returns the
structured action without touching the machine.

## Running simulation & the flagship

```powershell
uv run python -m autoflow_ai.cli mission simulate --live      # deterministic full loop, live trace
uv run python -m autoflow_ai.cli mission run "edit the document and save it" --file report.txt
```

## RAG / knowledge

```powershell
uv run python -m autoflow_ai.cli rag search "your query"
uv run python -m autoflow_ai.cli knowledge ingest examples\knowledge\hr_policy.md
```

## Web research (opt-in)

```powershell
$env:AUTOFLOW_ALLOW_WEB="1"
uv run python -m autoflow_ai.cli research run "latest python version" --allow-web --deep-read
```

## Backend API & real-time events

Start with `autoflow serve`. Endpoints and the SSE event contract are documented
in [`docs/API.md`](docs/API.md).

## Testing

```powershell
cd ai-ml
uv run python -m compileall -q src
uv run pytest -q                              # full suite
uv run pytest -q -k "not real_notepad and not real_word"   # skip slow real-desktop
```

Environment-gated live tests stay honestly **SKIPPED** unless the matching flag
is set (`AUTOFLOW_ALLOW_WEB`, `AUTOFLOW_REAL_WORD`, `AUTOFLOW_REAL_GMAIL`,
`AUTOFLOW_REAL_VISION`, `AUTOFLOW_LIVE_NVIDIA`, `AUTOFLOW_REAL_DESKTOP`).

## Security & secrets

`.env` is gitignored and never committed. Model weights, the model cache
(`.autoflow/`), runtime data, screenshots and mission stores are gitignored.
Secrets are redacted from logs, traces, datasets and events. See
[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Live capability matrix

See [`docs/CAPABILITY_MATRIX.md`](docs/CAPABILITY_MATRIX.md) for the exact
LIVE / INTEGRATION / SIMULATION / SKIPPED status of every capability.

## License

See repository license (if present). This is a local development project.
