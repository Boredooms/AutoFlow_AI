"""Structured edit operations applied deterministically to plain text.

Each operation is a typed, serializable transform. Applying an operation to a
string returns the new string plus a count of changes made. The document tools
apply these operations run-by-run to preserve DOCX structure/formatting.
"""

from __future__ import annotations

import re

from ..schemas.common import AutoFlowModel
from ..schemas.enums import StrEnum


class EditKind(StrEnum):
    """Kinds of deterministic text edits supported in this slice."""

    REPLACE_TEXT = "replace_text"          # literal find/replace
    NORMALIZE_EM_DASHES = "normalize_em_dashes"   # " - " / "--" -> em dash
    REMOVE_DOUBLE_SPACES = "remove_double_spaces"  # collapse runs of spaces
    FIX_SPACE_BEFORE_PUNCT = "fix_space_before_punct"  # "word ." -> "word."
    TRIM_TRAILING_WHITESPACE = "trim_trailing_whitespace"


# Common rule-based "grammar" fixes bundled under FIX_SPACE_BEFORE_PUNCT and
# REMOVE_DOUBLE_SPACES. Kept deliberately conservative and deterministic.

_EM_DASH = "\u2014"  # —


class EditOperation(AutoFlowModel):
    """One structured edit. ``find``/``replace`` used only by REPLACE_TEXT."""

    kind: EditKind
    find: str | None = None
    replace: str | None = None
    case_sensitive: bool = True

    def describe(self) -> str:
        if self.kind == EditKind.REPLACE_TEXT:
            return f"replace {self.find!r} -> {self.replace!r}"
        return self.kind.value


def _apply_replace(text: str, op: EditOperation) -> tuple[str, int]:
    if not op.find:
        return text, 0
    if op.case_sensitive:
        count = text.count(op.find)
        return (text.replace(op.find, op.replace or ""), count)
    # case-insensitive literal replace
    pattern = re.compile(re.escape(op.find), re.IGNORECASE)
    new_text, count = pattern.subn(op.replace or "", text)
    return new_text, count


def _apply_em_dashes(text: str) -> tuple[str, int]:
    # Normalize the common ASCII representations of an em dash:
    #   " -- "  -> " — "
    #   "--"    -> "—"
    #   " - "   -> " — "  (spaced hyphen used as a dash)
    count = 0
    new_text, n = re.subn(r"\s--\s", f" {_EM_DASH} ", text)
    count += n
    new_text, n = re.subn(r"--", _EM_DASH, new_text)
    count += n
    new_text, n = re.subn(r"(?<=\w) - (?=\w)", f" {_EM_DASH} ", new_text)
    count += n
    return new_text, count


def _apply_double_spaces(text: str) -> tuple[str, int]:
    # Collapse runs of 2+ spaces (not newlines/tabs) to a single space.
    matches = len(re.findall(r"  +", text))
    return re.sub(r"  +", " ", text), matches


def _apply_space_before_punct(text: str) -> tuple[str, int]:
    matches = len(re.findall(r"\s+([,.;:!?])", text))
    return re.sub(r"\s+([,.;:!?])", r"\1", text), matches


def _apply_trim_trailing(text: str) -> tuple[str, int]:
    lines = text.split("\n")
    changed = 0
    out = []
    for line in lines:
        stripped = line.rstrip()
        if stripped != line:
            changed += 1
        out.append(stripped)
    return "\n".join(out), changed


def apply_operation(text: str, op: EditOperation) -> tuple[str, int]:
    """Apply a single operation; return (new_text, change_count)."""

    if op.kind == EditKind.REPLACE_TEXT:
        return _apply_replace(text, op)
    if op.kind == EditKind.NORMALIZE_EM_DASHES:
        return _apply_em_dashes(text)
    if op.kind == EditKind.REMOVE_DOUBLE_SPACES:
        return _apply_double_spaces(text)
    if op.kind == EditKind.FIX_SPACE_BEFORE_PUNCT:
        return _apply_space_before_punct(text)
    if op.kind == EditKind.TRIM_TRAILING_WHITESPACE:
        return _apply_trim_trailing(text)
    raise ValueError(f"unsupported edit kind: {op.kind}")


def apply_operations(
    text: str, ops: list[EditOperation]
) -> tuple[str, list[tuple[str, int]]]:
    """Apply operations in order. Return (new_text, [(description, count), ...])."""

    report: list[tuple[str, int]] = []
    current = text
    for op in ops:
        current, count = apply_operation(current, op)
        report.append((op.describe(), count))
    return current, report


# Keyword -> operation detection for the deterministic slice. This is the
# rule-based stand-in for model-proposed edit operations; the architecture keeps
# EditOperation as the contract so a model can later produce the same objects.
def detect_operations_from_prompt(prompt: str) -> list[EditOperation]:
    """Infer edit operations from a natural-language prompt (rule-based)."""

    p = prompt.lower()
    ops: list[EditOperation] = []

    if "em-dash" in p or "em dash" in p or "emdash" in p:
        ops.append(EditOperation(kind=EditKind.NORMALIZE_EM_DASHES))
    if "double space" in p or "duplicate space" in p or "extra space" in p:
        ops.append(EditOperation(kind=EditKind.REMOVE_DOUBLE_SPACES))
    if "grammar" in p or "wording" in p or "clean up" in p or "clean-up" in p:
        # Conservative deterministic "grammar/wording" pass: fix stray spaces
        # before punctuation and collapse double spaces.
        ops.append(EditOperation(kind=EditKind.FIX_SPACE_BEFORE_PUNCT))
        ops.append(EditOperation(kind=EditKind.REMOVE_DOUBLE_SPACES))
    if "trailing" in p or "trim" in p:
        ops.append(EditOperation(kind=EditKind.TRIM_TRAILING_WHITESPACE))

    # Explicit replace: replace "X" with "Y"
    m = re.search(r'replace\s+"([^"]+)"\s+with\s+"([^"]+)"', prompt, re.IGNORECASE)
    if m:
        ops.append(
            EditOperation(kind=EditKind.REPLACE_TEXT, find=m.group(1), replace=m.group(2))
        )

    # De-duplicate while preserving order.
    seen = set()
    unique: list[EditOperation] = []
    for op in ops:
        key = op.to_json()
        if key not in seen:
            seen.add(key)
            unique.append(op)
    return unique
