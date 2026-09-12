# AutoFlow AI — Agent Brain and Orchestration

## 1. Architecture

The agent brain is not a single prompt. It is a coordinated runtime made from specialized decision layers.

```text
USER GOAL
   ↓
INTENT NORMALIZER
   ↓
CONTEXT / MEMORY RETRIEVAL
   ↓
PLANNER
   ↓
TASK GRAPH
   ↓
AGENT ASSIGNMENT
   ↓
MODEL ROUTING
   ↓
EXECUTION AGENT
   ↓
TOOL CALLING
   ↓
OBSERVE
   ↓
VERIFY
   ├── success → next step
   └── failure → recovery/replan
```

## 2. Initial agent system

### 2.1 Planner Agent

Question: **What is the whole job?**

Responsibilities:
- understand outcome;
- decompose work;
- identify dependencies;
- predict required capabilities;
- define expected states;
- define verification;
- mark approval boundaries.

### 2.2 Research Agent

Researches approved external/internal sources and produces evidence-backed structured findings.

### 2.3 Document Agent

Creates, edits, transforms and validates document artifacts.

### 2.4 Spreadsheet/Data Agent

Analyzes tabular data, performs transformations, calculations and produces validated outputs.

### 2.5 Presentation Agent

Builds and edits presentation artifacts while respecting structure and content requirements.

### 2.6 Coding Agent

Inspects repositories, proposes changes, edits through controlled tools, runs tests and prepares patches.

### 2.7 Communication Agent

Drafts messages and invokes send actions only through policy-approved communication tools.

### 2.8 Browser Automation Agent

Operates web applications using semantic browser tools, not arbitrary uncontrolled mouse movement.

### 2.9 Computer Automation Agent

Handles supported desktop workflows through UI Automation/application adapters and visual grounding fallback.

### 2.10 QA/Verification Agent

Independently checks whether expected conditions and artifacts are correct. It must be capable of rejecting an apparently successful execution.

## 3. Common agent contract

```python
AgentRunInput(
    task_id,
    step_id,
    objective,
    context,
    permissions,
    tool_schemas,
    observation,
    recovery_history,
    output_contract,
)
```

The return value must be typed.

## 4. Planner output

```json
{
  "goal":"...",
  "steps":[
    {
      "step_id":"step_01",
      "objective":"...",
      "agent":"research-agent",
      "dependencies":[],
      "preconditions":[],
      "expected_state":{},
      "verification":[],
      "risk":"low",
      "requires_approval":false
    }
  ]
}
```

## 5. Execution Agent

The executor answers:

> Given the current step, expected state, observed state, policy and recovery history, what is the next safe operation?

It must never receive only the original user request.

## 6. Context hierarchy

Use explicit boundaries:

```text
SYSTEM POLICY
TASK INSTRUCTION
AUTHORIZED CONTEXT
RETRIEVED KNOWLEDGE
CURRENT OBSERVATION
TOOL RESULTS
RECOVERY HISTORY
USER APPROVAL
```

Untrusted documents are data, not instructions.

## 7. Agent communication

Agents should communicate through structured artifacts/events rather than hidden conversational chains.

Example:

```json
{
  "from":"spreadsheet-agent",
  "to":"document-agent",
  "artifact":"artifact://report.xlsx",
  "verification":"passed",
  "notes":["totals reconciled"]
}
```

## 8. Parallel execution

Independent steps may run in parallel.

```text
           ┌→ Research A ─┐
Plan ──────┼→ Research B ─┼→ Synthesis
           └→ Data C ─────┘
```

Dependencies must be explicit. Active task state must never be implicitly shared across unrelated tasks.

## 9. Human-in-the-loop

The agent brain must generate approval requests when policy says the next operation is consequential.

Approval is an external state transition, not a natural-language hint.

## 10. Recovery-aware intelligence

Agent decisions must include bounded recovery information:

```text
attempt_number
failure_type
previous_tool
verification_failure
allowed_alternatives
remaining_budget
```

The executor should prefer local recovery over full-task replanning where possible.

## 11. Workflow memory

Only verified traces become reusable.

Canonical representations should look like:

```text
OpenReport()
SearchCustomer(name)
CreateDraft(template)
SaveDocument(path)
AttachFile(artifact_id)
SendEmail(recipient_group)
```

not raw screen coordinates.

## 12. Open-ended capability model

“General-purpose” means the agent brain can compose new workflows from available capabilities. It does not mean arbitrary, unrestricted machine access.

The platform expands through:

```text
NEW APPLICATION
   ↓
NEW TOOL / CONNECTOR
   ↓
NEW AGENT CAPABILITY
   ↓
VERIFIER
   ↓
POLICY
   ↓
WORKFLOW COMPOSITION
```

This provides a path from a fixed MVP to a much broader agentic execution platform.
