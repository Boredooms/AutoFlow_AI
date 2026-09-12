# AutoFlow AI — Execution Runtime

## 1. Responsibility

The execution runtime is the hands of AutoFlow AI. Models decide what should happen; deterministic runtime components perform approved operations.

## 2. Canonical execution loop

```text
LOAD STATE
  ↓
SELECT READY STEP
  ↓
RESOLVE CONTEXT
  ↓
ASK EXECUTION AGENT
  ↓
TOOL-CALL VALIDATION
  ↓
POLICY CHECK
  ↓
PERMISSION CHECK
  ↓
EXECUTE TOOL
  ↓
CAPTURE OBSERVATION
  ↓
VERIFY POSTCONDITIONS
  ├── PASS → CHECK NEXT STEP
  └── FAIL → RECOVERY
```

## 3. State machine

```text
QUEUED
  ↓
PLANNING
  ↓
VALIDATING
  ↓
AWAITING_APPROVAL
  ↓
RUNNING
  ↓
VERIFYING
  ├── COMPLETE
  └── RECOVERY
        ├── RETRY
        ├── RE-OBSERVE
        ├── RE-RESOLVE
        ├── ALTERNATE_PATH
        ├── REPLAN
        └── HUMAN_ESCALATION
```

Terminal states:
`COMPLETE`, `FAILED`, `CANCELLED`, `EXPIRED`, `BLOCKED`.

## 4. Tool definition

```json
{
  "name":"email.send",
  "description":"Send an email to approved recipients.",
  "input_schema":{},
  "risk_class":"high",
  "permission_scope":"communication:send",
  "requires_approval":true,
  "timeout_seconds":30,
  "idempotent":true,
  "verifier":"email.sent"
}
```

## 5. Tool runtime categories

### Files
Read/write/search/list/metadata.

### Documents
PDF/DOCX/PPTX/XLSX parsing, creation, editing and inspection.

### Browser
Navigate, click, type, select, extract, upload, download.

### Desktop
Inspect UI tree, resolve controls, click/type/select, switch windows, capture observation.

### Code
Sandboxed execution, testing, artifact generation and logs.

### Communication
Draft, attach, approve, send.

### Knowledge
Search authorized knowledge and retrieve verified workflows.

## 6. Permission model

A tool call is executable only when:

```text
TOOL EXISTS
AND
ARGUMENTS VALID
AND
TASK HAS TOOL
AND
USER HAS PERMISSION
AND
WORKSPACE POLICY ALLOWS
AND
RISK POLICY ALLOWS
AND
APPROVAL EXISTS WHEN REQUIRED
```

## 7. Computer automation

Preferred hierarchy:

```text
1. API/connector
2. Accessibility/UI Automation
3. DOM/semantic metadata
4. Application adapter
5. Visual grounding
6. Human escalation
```

Coordinates may be a temporary runtime detail, but are never the canonical workflow abstraction.

## 8. Visual grounding

Vision models should return semantic target candidates.

```json
{
  "role":"button",
  "name":"Save",
  "confidence":0.96,
  "region":{"x":...,"y":...,"w":...,"h":...}
}
```

The runtime must validate the target using available UI/application state before execution.

## 9. Verification

Verification categories:

- structural: schema/file exists;
- semantic: meaning/content correct;
- UI/state: expected application state reached;
- data: totals/rows/constraints reconcile;
- artifact: output opens/renders/contains required content.

Example:

```json
{
  "status":"passed",
  "checks":[
    {"id":"file_exists","passed":true},
    {"id":"schema_valid","passed":true},
    {"id":"content_check","passed":true}
  ],
  "evidence":["artifact://..."],
  "confidence":0.98
}
```

## 10. Recovery

```text
FAILURE
  ↓
TRANSIENT?
  ├─ yes → bounded retry
  └─ no
       ↓
RE-OBSERVE
       ↓
RE-RESOLVE TARGET
       ↓
ALTERNATE SAFE METHOD
       ↓
BOUNDED REPLAN
       ↓
HUMAN
```

Recovery is budgeted by:
- attempts;
- time;
- model calls;
- re-plans;
- tool cost where measurable.

## 11. Idempotency

Use execution/step/attempt identifiers where possible:

```text
execution_id + step_id + attempt_id
```

For external actions, the runtime should detect prior completion before retrying whenever the target system permits.

## 12. Cancellation

Cancellation must be persisted and checked before starting another side effect. Long-running tools must support cooperative cancellation where possible.

## 13. Artifact handling

Every generated artifact should carry:
- artifact ID;
- execution ID;
- workflow/version;
- source references;
- creator agent;
- verification state;
- content hash.

## 14. Audit event

Each significant operation must emit a normalized event with enough data to reconstruct what happened without exposing private chain-of-thought.

## 15. Runtime invariant

```text
NO LLM → DIRECT SIDE EFFECT
```

The only path is:

```text
LLM → STRUCTURED REQUEST → VALIDATION → POLICY → DETERMINISTIC RUNTIME → OBSERVATION → VERIFICATION
```
