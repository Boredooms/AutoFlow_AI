"""In-process mission registry driving the existing runtime + event bus.

Missions run through the SAME orchestration used by the CLI (society flagship /
simulation). The registry only coordinates + emits the canonical event stream;
it never re-implements agent logic. Simulation runs in a background thread so
the API can stream events while the mission executes.
"""

from __future__ import annotations

import tempfile
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .events import EventType, MissionEventBus


def _new_id(prefix: str = "exec") -> str:
    # prefix_token with NO extra underscore in the token (schema rule)
    token = datetime.now(timezone.utc).strftime("%H%M%S%f")
    return f"{prefix}_{prefix}{token}"


_STAGE_TO_EVENT = {
    "supervisor": EventType.TASK_DELEGATED,
    "rag": EventType.EVIDENCE_RETRIEVED,
    "planner": EventType.PLAN_CREATED,
    "research": EventType.OBSERVATION_CAPTURED,
    "document": EventType.ACTION_PROPOSED,
    "computer": EventType.ACTION_PROPOSED,
    "browser": EventType.ACTION_PROPOSED,
    "gmail": EventType.ACTION_PROPOSED,
    "verify": EventType.VERIFICATION_PASSED,
    "approval": EventType.APPROVAL_REQUESTED,
    "cleanup": EventType.CLEANUP_COMPLETED,
    "final": EventType.MISSION_COMPLETED,
}


@dataclass
class MissionRecord:
    mission_id: str
    prompt: str
    mode: str = "simulation"
    model: str = "auto"
    status: str = "created"              # created|running|awaiting_approval|complete|failed
    result: dict | None = None
    bus: MissionEventBus = field(default_factory=MissionEventBus)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict:
        return {
            "mission_id": self.mission_id, "prompt": self.prompt, "mode": self.mode,
            "model": self.model, "status": self.status, "created_at": self.created_at,
            "result": self.result,
        }


class MissionRegistry:
    """Creates, runs (simulation), and tracks missions + their event streams."""

    def __init__(self) -> None:
        self._missions: dict[str, MissionRecord] = {}
        self._lock = threading.Lock()

    def create(self, prompt: str, *, mode: str = "simulation", model: str = "auto") -> MissionRecord:
        mid = _new_id()
        rec = MissionRecord(mission_id=mid, prompt=prompt, mode=mode, model=model)
        with self._lock:
            self._missions[mid] = rec
        return rec

    def get(self, mission_id: str) -> MissionRecord | None:
        with self._lock:
            return self._missions.get(mission_id)

    def list(self) -> list[MissionRecord]:
        with self._lock:
            return list(self._missions.values())

    def run_simulation(self, rec: MissionRecord, *, await_approval: bool = False) -> None:
        """Run a deterministic flagship simulation, emitting canonical events."""

        rec.status = "running"
        rec.bus.emit(rec.mission_id, EventType.MISSION_STARTED, source="supervisor",
                     message=rec.prompt)

        from ..society import EmailSpec, simulate_mission

        tmp = Path(tempfile.mkdtemp())
        doc = tmp / "report.txt"
        doc.write_text("foo baseline report content", encoding="utf-8")
        att = tmp / "report_attachment.txt"
        att.write_text("attachment payload", encoding="utf-8")

        # stream each trace line as a canonical event as it happens
        def _sink(line: str) -> None:
            stage = line.split("]", 1)[0].strip("[").lower() if line.startswith("[") else "stage"
            etype = _STAGE_TO_EVENT.get(stage, EventType.STAGE)
            status = "waiting" if stage == "approval" else "info"
            rec.bus.emit(rec.mission_id, etype, source=stage, status=status, message=line)

        try:
            result = simulate_mission(
                document_prompt="edit the document and save it", document_path=str(doc),
                email=EmailSpec(recipient="reviewer@example.com", subject="Report",
                                body="Please find the report attached.", attachment_path=str(att)),
                execution_id=rec.mission_id, auto_approve=not await_approval, sink=_sink,
            )
        except Exception as exc:  # noqa: BLE001 - never crash the server thread
            rec.status = "failed"
            rec.bus.emit(rec.mission_id, EventType.MISSION_FAILED, status="fail",
                         message=type(exc).__name__)
            rec.bus.close()
            return

        rec.result = result.as_dict()
        if result.document_verified:
            rec.bus.emit(rec.mission_id, EventType.VERIFICATION_PASSED, source="verify",
                         status="ok", message="document independently verified")
            rec.bus.emit(rec.mission_id, EventType.ARTIFACT_CREATED, source="document",
                         status="ok", message="report.txt", payload={"name": "report.txt"})
        if result.outcome == "awaiting_approval":
            rec.status = "awaiting_approval"
            rec.bus.emit(rec.mission_id, EventType.APPROVAL_REQUESTED, source="gmail",
                         status="waiting", message="awaiting user approval before send")
        elif result.complete:
            rec.status = "complete"
            rec.bus.emit(rec.mission_id, EventType.MISSION_COMPLETED, source="final",
                         status="ok", message="mission complete and verified",
                         payload={"agenticity": result.agenticity})
        else:
            rec.status = "failed"
            rec.bus.emit(rec.mission_id, EventType.MISSION_FAILED, status="fail",
                         message=result.reason)
        rec.bus.close()

    def run_simulation_async(self, rec: MissionRecord, *, await_approval: bool = False) -> None:
        t = threading.Thread(target=self.run_simulation, args=(rec,),
                             kwargs={"await_approval": await_approval}, daemon=True)
        t.start()
