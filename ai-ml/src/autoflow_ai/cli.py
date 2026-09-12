"""AutoFlow AI headless CLI.

The entire AI/ML system must be testable without Electron. This CLI is the
headless entry point. Phase 1 provides:

    autoflow version                 # print versions
    autoflow contracts list          # list all registered contract models
    autoflow contracts check         # self-check: build + round-trip samples
    autoflow phase status            # show implementation phase ledger
    autoflow eval smoke              # fast end-to-end contract smoke test

Later phases attach their own subcommands (task, plan, workflow, tool, memory,
eval golden/chaos/benchmark) to the same parser.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Callable

from . import CONTRACTS_VERSION, __version__
from . import schemas as S
from .samples import build_sample_registry


def _print(obj: object) -> None:
    if isinstance(obj, str):
        print(obj)
    else:
        print(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False))


# ---------------------------------------------------------------------------
# command handlers
# ---------------------------------------------------------------------------


def cmd_version(_: argparse.Namespace) -> int:
    _print(
        {
            "autoflow_ai": __version__,
            "contracts_version": CONTRACTS_VERSION,
            "python": sys.version.split()[0],
        }
    )
    return 0


def cmd_contracts_list(_: argparse.Namespace) -> int:
    names = sorted(n for n in S.__all__ if n[0].isupper())
    _print({"count": len(names), "contracts": names})
    return 0


def cmd_contracts_check(_: argparse.Namespace) -> int:
    """Build every sample contract and round-trip it through JSON.

    A failure here means a contract is broken. Returns non-zero on any error.
    """

    registry = build_sample_registry()
    failures: list[dict] = []
    checked = 0
    for name, instance in registry.items():
        checked += 1
        try:
            cls = type(instance)
            payload = instance.model_dump(mode="json")
            restored = cls.model_validate(payload)
            if restored.to_json() != instance.to_json():
                failures.append({"contract": name, "error": "round-trip mismatch"})
        except Exception as exc:  # noqa: BLE001 - report any contract failure
            failures.append({"contract": name, "error": repr(exc)})

    result = {
        "checked": checked,
        "passed": checked - len(failures),
        "failed": len(failures),
        "failures": failures,
    }
    _print(result)
    return 1 if failures else 0


def cmd_phase_status(_: argparse.Namespace) -> int:
    ledger = {
        "current_phase": 1,
        "phase_1": "contract layer — implemented",
        "next_phase": 2,
        "note": "see docs/IMPLEMENTATION_STATUS.md for the full ledger",
    }
    _print(ledger)
    return 0


def cmd_eval_smoke(_: argparse.Namespace) -> int:
    """End-to-end contract smoke test runnable from the CLI.

    Exercises the primary flow shapes: normalize -> plan (DAG) -> tool call ->
    observation -> verification -> approval binding. Returns non-zero on any
    inconsistency.
    """

    from .samples import smoke_flow

    report = smoke_flow()
    _print(report)
    return 0 if report.get("ok") else 1


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoflow",
        description="AutoFlow AI headless CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_version = sub.add_parser("version", help="print version info")
    p_version.set_defaults(func=cmd_version)

    p_contracts = sub.add_parser("contracts", help="contract layer commands")
    csub = p_contracts.add_subparsers(dest="subcommand", required=True)
    c_list = csub.add_parser("list", help="list all contract models")
    c_list.set_defaults(func=cmd_contracts_list)
    c_check = csub.add_parser("check", help="build + round-trip all contracts")
    c_check.set_defaults(func=cmd_contracts_check)

    p_phase = sub.add_parser("phase", help="phase status")
    psub = p_phase.add_subparsers(dest="subcommand", required=True)
    p_status = psub.add_parser("status", help="show phase ledger")
    p_status.set_defaults(func=cmd_phase_status)

    p_eval = sub.add_parser("eval", help="evaluation harness")
    esub = p_eval.add_subparsers(dest="subcommand", required=True)
    e_smoke = esub.add_parser("smoke", help="fast end-to-end contract smoke test")
    e_smoke.set_defaults(func=cmd_eval_smoke)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func: Callable[[argparse.Namespace], int] = args.func
    return func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
